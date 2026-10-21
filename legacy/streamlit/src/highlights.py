import streamlit as st
import datetime
import pandas as pd
from pathlib import Path
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Tuple, Union, Any
import re
import json
import concurrent.futures
import threading
from functools import partial
import time
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import pyttsx3
import io
import base64
import zipfile
from io import BytesIO
import os
import tempfile
import traceback
import logging
import shutil
import subprocess
import sys
import platform

# Import video extraction function from utils
from utils.video_extractor import create_highlights_compilation
from utils.enhanced_display import display_highlights_in_streamlit as display_highlights_enhanced

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add FFmpeg to PATH if on Windows
def setup_ffmpeg_path():
    if platform.system() == 'Windows':
        # Common FFmpeg installation paths on Windows
        possible_paths = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin"
        ]
        
        for path in possible_paths:
            if os.path.isdir(path) and path not in os.environ['PATH']:
                os.environ['PATH'] = f"{path};{os.environ['PATH']}"
                break

# Setup FFmpeg path at module load
setup_ffmpeg_path()

def load_llm():
    """Load LLM using the provider factory to avoid circular dependencies."""
    from core.llm_provider import LLMProviderFactory
    try:
        provider = LLMProviderFactory.create_provider()
        return provider._get_llm()
    except Exception as e:
        print(f"Failed to load LLM: {e}")
        # Fallback to original method if needed
        try:
            from app import load_llm as _load_llm
            return _load_llm()
        except:
            return None

def parse_timestamp(timestamp_str: str) -> int:
    """
    Convert timestamp string to seconds.
    Handles formats: MM:SS, MM:SS:00, HH:MM:SS
    """
    if not timestamp_str or pd.isna(timestamp_str):
        return 0
    
    # Clean the timestamp string
    timestamp_str = str(timestamp_str).strip()
    
    # Handle different timestamp formats
    if ':' in timestamp_str:
        parts = timestamp_str.split(':')
        
        if len(parts) == 2:  # MM:SS
            try:
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes * 60 + seconds
            except ValueError:
                return 0
                
        elif len(parts) == 3:  # HH:MM:SS or MM:SS:MS
            try:
                if int(parts[0]) > 23:  # Likely MM:SS:MS format
                    minutes, seconds = int(parts[0]), int(parts[1])
                    return minutes * 60 + seconds
                else:  # HH:MM:SS format
                    hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                    return hours * 3600 + minutes * 60 + seconds
            except ValueError:
                return 0
    
    # Try to extract numbers if format is unclear
    numbers = re.findall(r'\d+', timestamp_str)
    if len(numbers) >= 2:
        return int(numbers[0]) * 60 + int(numbers[1])
    
    return 0

def format_timestamp(seconds: int) -> str:
    """Convert seconds back to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def calculate_excitement_score(rally: Dict, sport_adapter=None) -> float:
    """
    Calculate excitement score for a rally based on multiple factors.
    Higher score = more exciting for highlights.
    Returns a score between 0 and 10.
    """
    print(f"[DEBUG] Calculating excitement score for rally: {rally}")
    score = 0.0
    
    try:
        # Get sport-specific configuration if available
        exciting_shots = {
            'smash': 1.0,
            'jump smash': 1.5,
            'around the head': 1.2,
            'tumbling net shot': 1.3,
            'dive': 1.4,
            'cross-court net shot': 1.1,
            'backhand smash': 1.2
        }
        win_bonuses = {
            'smash': 0.8,
            'drop': 0.5,
            'net shot': 0.6,
            'clear': 0.3,
            'drive': 0.4
        }
        max_score = 21  # Default for badminton
        
        # Override with sport-specific config if available
        if sport_adapter and hasattr(sport_adapter, 'config'):
            config = sport_adapter.config
            if hasattr(config, 'analysis'):
                exciting_shots = getattr(config.analysis, 'exciting_shots', exciting_shots)
                win_bonuses = getattr(config.analysis, 'win_bonuses', win_bonuses)
            if hasattr(config, 'game_structure'):
                max_score = getattr(config.game_structure, 'max_score', max_score)
        
        # Base score for rally length (longer rallies are generally more exciting)
        start_time = parse_timestamp(rally.get('start_time', '0:00'))
        end_time = parse_timestamp(rally.get('end_time', '0:00'))
        duration = max(1, end_time - start_time)
        duration_score = min(duration / 10.0, 3.0)  # Cap at 3 points for very long rallies
        score += duration_score
        print(f"[DEBUG] Duration: {duration}s, Score: +{duration_score:.2f}")
        
        # Score based on ball types (more variety = more exciting)
        ball_types = rally.get('ball_types', '').lower()
        unique_shots = set([bt.strip() for bt in ball_types.split(',') if bt.strip()])
        shot_variety = min(len(unique_shots) * 0.75, 2.5)  # Cap at 2.5 points for shot variety
        score += shot_variety
        print(f"[DEBUG] Unique shots: {unique_shots}, Score: +{shot_variety:.2f}")
        
        # Bonus for specific exciting shots (from sport config)
        shot_bonus = 0
        for shot, bonus in exciting_shots.items():
            if shot in ball_types:
                shot_bonus += bonus
                print(f"[DEBUG] Exciting shot detected: {shot}, Bonus: +{bonus:.2f}")
        
        # Cap shot bonus to avoid over-scoring
        shot_bonus = min(shot_bonus, 2.5)
        score += shot_bonus
        
        # Bonus for close scores (more exciting matches)
        try:
            score_a = int(rally.get('roundscore_A', '0'))
            score_b = int(rally.get('roundscore_B', '0'))
            score_diff = abs(score_a - score_b)
            
            if score_diff <= 2:  # Close game
                close_game_bonus = 1.5 - (score_diff * 0.25)  # 1.5 for tie, 1.25 for 1pt diff, 1.0 for 2pt diff
                score += close_game_bonus
                print(f"[DEBUG] Close game ({score_a}-{score_b}), Bonus: +{close_game_bonus:.2f}")
        except (ValueError, TypeError) as e:
            print(f"[WARNING] Error calculating close game bonus: {e}")
        
        # Bonus for match point situations
        try:
            if int(rally.get('roundscore_A', 0)) >= (max_score - 1) or int(rally.get('roundscore_B', 0)) >= (max_score - 1):
                match_point_bonus = 1.5
                score += match_point_bonus
                print(f"[DEBUG] Match point situation, Bonus: +{match_point_bonus:.2f}")
        except (ValueError, TypeError) as e:
            print(f"[WARNING] Error calculating match point bonus: {e}")
        
        # Bonus for winning shot type (from sport config)
        win_reason = rally.get('win_reason', '').lower()
        
        for shot_type, bonus in win_bonuses.items():
            if shot_type in win_reason:
                score += bonus
                print(f"[DEBUG] Winning shot: {shot_type}, Bonus: +{bonus:.2f}")
                break
        
        # Ensure score is within bounds
        final_score = max(0, min(score, 10.0))
        print(f"[DEBUG] Final excitement score: {final_score:.2f}/10.0")
        return final_score
        
    except Exception as e:
        print(f"[ERROR] Error in calculate_excitement_score: {str(e)}")
        return 5.0  # Default average score if there's an error

def analyze_rally_with_ai(rally: Dict, llm, sport_adapter=None) -> Dict:
    """Analyze a rally using AI to enhance the excitement score."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    
    # Get sport-specific AI analysis prompt from config
    prompt_template = """
Analyze this badminton rally and explain why it deserves to be a highlight in exactly 120 words or less.
Focus on what made this rally exciting and spectacular for viewers.

Consider these factors:
- Shot variety and complexity (smashes, drops, net kills, deceptive shots)
- Player movement and court coverage (diving saves, quick recoveries)
- Rally length and intensity (long exchanges, high pace)
- Technical brilliance (perfect placement, power, timing)
- Dramatic moments (comeback shots, impossible saves)
- Entertainment value for spectators

Rally Data:
{rally_data}

Return a JSON with:
- score: number from 0-10 (excitement level)
- reasoning: explain in 60 words why this rally is highlight-worthy, focusing on the spectacular moments, technical skills, and entertainment value that make viewers excited
- highlight_worthy: boolean
"""
    
    # Override with sport-specific prompt if available
    if sport_adapter and hasattr(sport_adapter, 'config'):
        config = sport_adapter.config
        if hasattr(config, 'analysis'):
            # Try highlights_prompt first, then fallback to ai_analysis_prompt
            sport_prompt = getattr(config.analysis, 'highlights_prompt', None)
            if not sport_prompt:
                sport_prompt = getattr(config.analysis, 'ai_analysis_prompt', None)
            if sport_prompt:
                prompt_template = sport_prompt
    
    # Format rally data for the prompt
    rally_data = "\n".join(f"{k}: {v}" for k, v in rally.items())
    
    # Create the chain
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        # Get AI analysis
        result = chain.invoke({"rally_data": rally_data})
        
        # Update rally with AI analysis
        rally['ai_score'] = float(result.get('score', 0))
        rally['ai_reasoning'] = result.get('reasoning', '')
        rally['highlight_worthy'] = result.get('highlight_worthy', False)
        
    except Exception as e:
        print(f"AI analysis failed: {e}")
        # Fallback to original score if AI fails
        rally['ai_score'] = rally.get('excitement_score', 0) / 10  # Scale 0-10
        rally['ai_reasoning'] = "AI analysis unavailable"
        rally['highlight_worthy'] = rally.get('excitement_score', 0) > 5
    
    return rally

def parallel_calculate_excitement_scores(rallies: List[Dict], sport_adapter=None, max_workers: int = None) -> List[Dict]:
    """Calculate excitement scores for multiple rallies in parallel."""
    if not rallies:
        return []
    
    # Determine optimal number of workers
    if max_workers is None:
        max_workers = min(len(rallies), 8)  # Cap at 8 to avoid overwhelming the system
    
    print(f"[PARALLEL] Calculating excitement scores for {len(rallies)} rallies using {max_workers} workers")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all rally scoring tasks
        future_to_rally = {
            executor.submit(calculate_excitement_score, rally, sport_adapter): i 
            for i, rally in enumerate(rallies)
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_rally):
            rally_index = future_to_rally[future]
            try:
                score = future.result()
                rallies[rally_index]['excitement_score'] = score
            except Exception as e:
                print(f"[ERROR] Failed to calculate excitement score for rally {rally_index}: {e}")
                rallies[rally_index]['excitement_score'] = 5.0  # Default score
    
    elapsed = time.time() - start_time
    print(f"[PARALLEL] Completed excitement scoring in {elapsed:.2f}s")
    return rallies

def parallel_ai_analysis(rallies: List[Dict], llm, sport_adapter=None, max_workers: int = None) -> List[Dict]:
    """Perform AI analysis on multiple rallies in parallel."""
    if not rallies:
        return []
    
    # Determine optimal number of workers (fewer for AI calls to avoid rate limits)
    if max_workers is None:
        max_workers = min(len(rallies), 4)  # Cap at 4 for AI calls
    
    print(f"[PARALLEL] Running AI analysis for {len(rallies)} rallies using {max_workers} workers")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all AI analysis tasks
        future_to_rally = {
            executor.submit(analyze_rally_with_ai, rally.copy(), llm, sport_adapter): i 
            for i, rally in enumerate(rallies)
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_rally):
            rally_index = future_to_rally[future]
            try:
                analyzed_rally = future.result()
                # Update the original rally with AI analysis results
                rallies[rally_index].update({
                    'ai_score': analyzed_rally.get('ai_score', 0),
                    'ai_reasoning': analyzed_rally.get('ai_reasoning', ''),
                    'highlight_worthy': analyzed_rally.get('highlight_worthy', False)
                })
            except Exception as e:
                print(f"[ERROR] Failed AI analysis for rally {rally_index}: {e}")
                # Set fallback values
                rallies[rally_index].update({
                    'ai_score': rallies[rally_index].get('excitement_score', 5.0) / 10,
                    'ai_reasoning': "AI analysis failed",
                    'highlight_worthy': rallies[rally_index].get('excitement_score', 5.0) > 5
                })
    
    elapsed = time.time() - start_time
    print(f"[PARALLEL] Completed AI analysis in {elapsed:.2f}s")
    return rallies

def select_highlights(rallies_data: Union[List[Dict], str], sport_adapter: Any, min_highlights: int = 7, min_duration: int = 3, max_highlights: int = 15) -> List[Dict]:
    """
    Select the best rallies for highlights using a combination of
    rule-based and AI-based scoring.

    Args:
        rallies_data: Can be a list of dicts, a string of JSON, or a string of rally data
        sport_adapter: Sport adapter for sport-specific configuration
        min_highlights: Minimum number of highlights to return
        min_duration: Minimum duration in seconds for a rally to be considered
        max_highlights: Maximum number of highlights to return (default: 15)
    """
    print("\n" + "="*80)
    print("SELECT_HIGHLIGHTS: Starting highlight selection process")
    print(f"[DEBUG] Input rallies_data type: {type(rallies_data)}")

    # Convert input to list of dictionaries if needed
    processed_rallies = []

    if not rallies_data:
        print("[ERROR] No rally data provided to select_highlights")
        return []

    # Handle string input (JSON or text format)
    if isinstance(rallies_data, str):
        print("[DEBUG] Processing string input...")
        try:
            # Try to parse as JSON
            parsed = json.loads(rallies_data)
            if isinstance(parsed, list):
                processed_rallies = parsed
                print(f"[DEBUG] Successfully parsed {len(processed_rallies)} rallies from JSON string")
            else:
                print("[DEBUG] JSON is not a list, trying to parse as text format...")
                processed_rallies = parse_rallies_from_text(rallies_data)
        except json.JSONDecodeError:
            print("[DEBUG] Not valid JSON, trying to parse as text format...")
            processed_rallies = parse_rallies_from_text(rallies_data)
    # Handle list input
    elif isinstance(rallies_data, list):
        print("[DEBUG] Processing list input...")
        # If list contains strings, try to parse each one
        if rallies_data and isinstance(rallies_data[0], str):
            processed_rallies = []
            for item in rallies_data:
                try:
                    parsed = json.loads(item)
                    if isinstance(parsed, dict):
                        processed_rallies.append(parsed)
                except (json.JSONDecodeError, TypeError):
                    print(f"[WARNING] Could not parse item: {item[:100]}...")
        else:
            # List already contains dictionaries
            processed_rallies = rallies_data
    else:
        print(f"[ERROR] Unsupported rallies_data type: {type(rallies_data)}")
        return []

    if not processed_rallies:
        print("[ERROR] No valid rally data found after processing")
        return []

    print(f"[DEBUG] Processing {len(processed_rallies)} rallies for highlight selection")

    # Step 1: Calculate excitement scores in parallel
    print("\n[PARALLEL] Step 1: Calculating excitement scores...")
    processed_rallies = parallel_calculate_excitement_scores(processed_rallies, sport_adapter)

    # Step 2: Run AI analysis in parallel (optional, can be disabled for speed)
    print("\n[PARALLEL] Step 2: Running AI analysis...")
    try:
        # Create LLM provider
        from core.llm_provider import LLMProviderFactory
        llm_provider = LLMProviderFactory.create_provider()
        llm = llm_provider._get_llm()
        processed_rallies = parallel_ai_analysis(processed_rallies, llm, sport_adapter)
    except Exception as e:
        print(f"[WARNING] AI analysis failed: {e}. Continuing with rule-based scoring only.")

    # Step 3: Calculate combined scores and filter
    print("\n[DEBUG] Calculating combined scores...")
    for rally in processed_rallies:
        base_score = float(rally.get('excitement_score', 5.0))
        raw_ai_score = rally.get('ai_score', None)
        
        # Normalize AI score to 0-10 scale
        if raw_ai_score is None:
            ai_score_10 = base_score
        elif raw_ai_score <= 1.0 and base_score > 1.0:
            ai_score_10 = raw_ai_score * 10.0
        else:
            ai_score_10 = float(raw_ai_score)

        # Combine scores (70% rule-based, 30% AI-based on consistent 0-10 scale)
        combined_score = (base_score * 0.7) + (ai_score_10 * 0.3)
        rally['combined_score'] = combined_score

        print(f"[DEBUG] Rally {rally.get('start_time', 'N/A')}-{rally.get('end_time', 'N/A')}: Base={base_score:.2f}, AI={ai_score_10:.2f}, Combined={combined_score:.2f}")

    # Step 4: Sort by combined score and filter by duration
    print("\n[DEBUG] Sorting rallies by combined score...")

    # Filter by minimum duration
    duration_filtered = []
    for rally in processed_rallies:
        start_time = parse_timestamp(rally.get('start_time', '0:00'))
        end_time = parse_timestamp(rally.get('end_time', '0:00'))
        duration = end_time - start_time

        if duration >= min_duration:
            rally['duration'] = duration
            duration_filtered.append(rally)

    # Sort by combined score (highest first)
    sorted_rallies = sorted(duration_filtered, key=lambda x: x.get('combined_score', 0), reverse=True)

    print(f"\n[DEBUG] Top {min(len(sorted_rallies), 10)} rallies by score:")
    for i, rally in enumerate(sorted_rallies[:10], 1):
        duration = rally.get('duration', 0)
        score = rally.get('combined_score', 0)
        start_time = rally.get('start_time', 'N/A')
        end_time = rally.get('end_time', 'N/A')
        winner = rally.get('win_point_player', 'N/A')
        shots = rally.get('ball_types', 'N/A')
        print(f"{i}. {start_time}-{end_time} ({duration}s) - Score: {score:.2f} - {winner} - {shots}")

    # Select top highlights (limit to max_highlights)
    selected_highlights = sorted_rallies[:max_highlights]

    print(f"\n[DEBUG] Total scored rallies: {len(processed_rallies)}")
    print(f"[DEBUG] AI highlight-worthy rallies: {len([r for r in processed_rallies if r.get('highlight_worthy', False)])}")
    print(f"[DEBUG] STRICT LIMIT APPLIED: Selected exactly {len(selected_highlights)} highlights (max requested: {max_highlights})")

    print(f"\n[DEBUG] Processing AI-recommended highlights...")
    print(f"[DEBUG] select_highlights returned {len(selected_highlights)} highlights")

    return selected_highlights

def remove_emojis(text: str) -> str:
    """Remove emojis and other special characters from text."""
    import re
    if not text:
        return text
    
    # Simple approach to remove common emojis and symbols
    # Remove characters in common emoji ranges
    cleaned_text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # emoticons
    cleaned_text = re.sub(r'[\U0001F300-\U0001F5FF]', '', cleaned_text)  # symbols & pictographs
    cleaned_text = re.sub(r'[\U0001F680-\U0001F6FF]', '', cleaned_text)  # transport & map
    cleaned_text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', cleaned_text)  # flags
    cleaned_text = re.sub(r'[\U00002702-\U000027B0]', '', cleaned_text)  # dingbats
    cleaned_text = re.sub(r'[\U000024C2-\U0001F251]', '', cleaned_text)  # enclosed chars
    
    return cleaned_text

def format_time(time_str: str) -> str:
    """Format time from MM:SS to natural language."""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        parts = []
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        return ' '.join(parts)
    except (ValueError, AttributeError):
        return time_str

def convert_to_natural_time(time_str: str) -> str:
    """Convert MM:SS format to natural language (e.g., '07:30' -> '7 minutes 30 seconds')."""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        parts = []
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:  # Always show at least seconds if no minutes
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        return ' '.join(parts)
    except (ValueError, AttributeError):
        return time_str

def create_narrative_highlight(rally: Dict, index: int, player_names: str = "the players") -> str:
    """Convert rally data into a natural language narrative."""
    start_time = rally.get('start_time', '00:00')
    end_time = rally.get('end_time', '00:00')
    win_player = rally.get('win_point_player', 'a player')
    ball_types = rally.get('ball_types', 'shot')
    
    # Convert times to natural language
    natural_start = convert_to_natural_time(start_time)
    
    # Convert ball types to natural language
    if isinstance(ball_types, str):
        shots = [s.strip().lower() for s in ball_types.split(',') if s.strip()]
        if not shots:
            shots = ['shot']
    else:
        shots = ['shot']
    
    # Create shot descriptions
    if len(shots) > 1:
        shot_desc = ", ".join(shots[:-1]) + ", and " + shots[-1]
    else:
        shot_desc = shots[0]
    
    # Create narrative templates without emojis
    templates = [
        f"At {natural_start} into the match, {win_player} takes the lead with an impressive sequence of {shot_desc} to win the point.",
        f"Highlight {index} at {natural_start} shows {win_player} demonstrating great skill with {shot_desc} to secure the point.",
        f"A fantastic rally at {natural_start} sees {win_player} outmaneuver their opponent with {shot_desc}.",
        f"{win_player} shows excellent technique at {natural_start}, using {shot_desc} to win the point.",
        f"The action at {natural_start} features {win_player} executing perfect {shot_desc} to take the point."
    ]
    
    # Add AI reasoning if available - no word limit
    ai_reason = rally.get('ai_reasoning', '')
    if ai_reason and ai_reason != "AI analysis unavailable":
        # Remove any emojis from AI reason
        ai_reason = remove_emojis(ai_reason)
        templates[0] += " " + ai_reason
    
    # Randomly select a template for variety
    import random
    return random.choice(templates) + " "

def parse_rallies_from_text(text: str) -> List[Dict]:
    """
    Parse rally data from text format into a list of dictionaries.
    Handles various text formats including:
    - JSON strings
    - Key-value pairs separated by newlines
    - Log-formatted rally data
    """
    if not text or not isinstance(text, str):
        return []
    
    # Try to parse as JSON first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
    except json.JSONDecodeError:
        pass
    
    # Try to parse log-formatted rally data
    rally_entries = []
    current_rally = {}
    
    # Check if this is a log-formatted string with multiple rallies
    if 'Rally data processed successfully' in text or 'Processed rally' in text:
        # Extract just the rally data part
        rally_blocks = re.split(r'\[DEBUG\] Processed rally \d+:', text)
        if len(rally_blocks) > 1:
            for block in rally_blocks[1:]:  # Skip the first block (header)
                try:
                    # Clean up the block and parse as JSON
                    clean_block = block.strip()
                    if not clean_block or clean_block == '{}':
                        continue
                        
                    # Handle single quotes in the string
                    clean_block = clean_block.replace("'", '"')
                    # Handle Python's None -> null
                    clean_block = clean_block.replace('None', 'null')
                    
                    rally = json.loads(clean_block)
                    if isinstance(rally, dict):
                        rally_entries.append(rally)
                except json.JSONDecodeError as e:
                    print(f"[WARNING] Could not parse rally block: {e}\nBlock: {block}")
                    continue
        
        if rally_entries:
            return rally_entries
    
    # Fall back to key-value pair parsing if log parsing didn't work
    rallies = []
    current_rally = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check for new rally marker
        if line.lower().startswith('rally') or line.startswith('{') or line.startswith('['):
            if current_rally:  # Save previous rally
                rallies.append(current_rally)
                current_rally = {}
            continue
            
        # Try to parse key-value pairs
        if ':' in line:
            try:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Clean up common formatting issues
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                    
                current_rally[key] = value
            except (ValueError, AttributeError):
                print(f"[WARNING] Could not parse line: {line}")
    
    # Add the last rally if exists
    if current_rally:
        rallies.append(current_rally)
    
    # Validate rallies have required fields
    required_fields = {'start_time', 'end_time', 'win_point_player', 'ball_types'}
    valid_rallies = []
    
    for rally in rallies:
        if not isinstance(rally, dict):
            continue
            
        # Ensure all required fields are present and not empty
        if all(field in rally and rally[field] for field in required_fields):
            valid_rallies.append(rally)
    
    print(f"[DEBUG] Parsed {len(valid_rallies)} valid rallies from text")
    return valid_rallies

def display_highlights_in_streamlit(generation: str, selected_highlights: List[Dict], player_names: str, sport_name: str = "Sports", video_url: str = None):
    """
    Display highlights content in Streamlit web interface with proper formatting.
    Now supports video embedding with AI narration when video_url is provided.
    """
    # Use the enhanced display function from utils
    return display_highlights_enhanced(generation, selected_highlights, player_names, sport_name, video_url)

def generate_highlights_response(state: Dict) -> Dict:
    """
    Generates clean highlights output with exact timestamps from pre-processed rally data.
    Handles various input formats and ensures proper data validation.
    NOW WITH PROPER WEB DISPLAY INTEGRATION.
    """
    try:
        print("\n" + "="*80)
        print("GENERATE_HIGHLIGHTS_RESPONSE: Starting highlights generation...")
        print(f"[DEBUG] State keys: {list(state.keys())}")
        
        # Get sport adapter from state
        sport_adapter = state.get('sport_adapter')
        if not sport_adapter:
            error_msg = "No sport adapter found. Please select a sport before analyzing."
            print(f"[ERROR] {error_msg}")
            st.error(error_msg)
            return {"generation": error_msg}
        
        # Extract player names from state
        player_names = state.get('player_names', 'Player 1 vs Player 2')
        print(f"[DEBUG] Player names: {player_names}")

        # Get event data from state (generic instead of rally_data)
        event_data = state.get('event_data', [])
        print(f"[DEBUG] Initial event_data type: {type(event_data)}")

        # If we don't have event_data, try to get it from semantics_analysis
        if not event_data and 'semantics_analysis' in state:
            print("[DEBUG] No event_data, checking semantics_analysis...")
            event_data = state['semantics_analysis']
            print(f"[DEBUG] Got event_data from semantics_analysis, type: {type(event_data)}")

            # If it's a dict, try to extract event data
            if isinstance(event_data, dict):
                if 'events' in event_data:
                    event_data = event_data['events']
                elif 'event_data' in event_data:
                    event_data = event_data['event_data']
                print(f"[DEBUG] Extracted event_data from dict, type: {type(event_data)}")

        # Process the event data to ensure it's in the correct format
        if not event_data:
            error_msg = "No event data found. Please check your input data."
            print(f"[ERROR] {error_msg}")
            st.error(error_msg)
            return {"generation": error_msg}

        # Try to extract event data from various possible formats
        processed_events = []

        # Case 1: event_data is already a list of dictionaries
        if isinstance(event_data, list) and all(isinstance(x, dict) for x in event_data):
            print("[DEBUG] Found list of dicts in event_data")
            processed_events = event_data

        # Case 2: event_data is a dictionary with an 'events' key
        elif isinstance(event_data, dict) and 'events' in event_data and isinstance(event_data['events'], list):
            print("[DEBUG] Found 'events' key in event_data dict")
            processed_events = event_data['events']

        # Case 3: event_data is a single event dictionary
        elif isinstance(event_data, dict):
            print("[DEBUG] Found single event dict")
            processed_events = [event_data]

        # Case 4: event_data is a string that might contain JSON or log data
        elif isinstance(event_data, str):
            print("[DEBUG] Attempting to parse event_data as string")
            try:
                parsed = json.loads(event_data)
                if isinstance(parsed, list):
                    processed_events = parsed
                elif isinstance(parsed, dict):
                    if 'events' in parsed and isinstance(parsed['events'], list):
                        processed_events = parsed['events']
                    else:
                        processed_events = [parsed]
                print(f"[DEBUG] Successfully parsed {len(processed_events)} events from JSON string")
            except json.JSONDecodeError:
                print("[DEBUG] JSON parse failed, trying text parser")
                processed_events = parse_rallies_from_text(event_data)

        # Validate and process the events using sport adapter
        sport_config = sport_adapter.config if sport_adapter else None
        required_fields = set(sport_config.required_columns.keys()) if sport_config else {'start_time', 'end_time'}

        valid_events = []

        for i, event in enumerate(processed_events, 1):
            if not isinstance(event, dict):
                print(f"[WARNING] Event {i} is not a dictionary, skipping")
                continue

            # Check for required fields - more flexible validation
            missing_fields = []
            for field in required_fields:
                value = event.get(field)
                if value is None or value == '' or value == [] or (isinstance(value, str) and value.strip() == ''):
                    missing_fields.append(field)

            if missing_fields:
                print(f"[WARNING] Event {i} is missing required fields {missing_fields}")
                # Try to extract missing fields from other fields if possible (sport-specific)
                if sport_adapter:
                    try:
                        if sport_adapter.validate_event_data(event):
                            # Add default values for missing optional fields
                            for field in missing_fields:
                                if field in required_fields:
                                    event[field] = event.get(field, 'Unknown')
                        else:
                            continue
                    except:
                        continue
                else:
                    continue

            # Process timestamps
            try:
                # Convert timestamp strings to seconds
                start_time = parse_timestamp(str(event.get('start_time', '00:00')))
                end_time = parse_timestamp(str(event.get('end_time', '00:30')))

                # Validate timestamps
                if start_time is None or end_time is None:
                    print(f"[WARNING] Could not parse timestamps in event {i}")
                    continue

                if end_time <= start_time:
                    print(f"[WARNING] Invalid time range in event {i}")
                    continue

                # Add calculated fields
                event['start_seconds'] = start_time
                event['end_seconds'] = end_time
                event['duration'] = end_time - start_time

                # Use sport adapter to get key metrics
                if sport_adapter:
                    metrics = sport_adapter.get_key_metrics(event)
                    event.update(metrics)

                valid_events.append(event)
                print(f"[DEBUG] Added valid event {i}: {event.get('start_time', '00:00')} - {event.get('end_time', '00:30')} ({event.get('duration', 0)}s)")

            except Exception as e:
                print(f"[WARNING] Error processing event {i}: {str(e)}")
                continue

        if not valid_events:
            error_msg = f"No valid events found after processing. Required fields: {', '.join(required_fields)}"
            print(f"[ERROR] {error_msg}")
            st.error(error_msg)
            return {"generation": error_msg}

        print(f"[DEBUG] Found {len(valid_events)} valid events after processing")

        # Update state with processed events
        state['event_data'] = valid_events
            
        # Select highlights with error handling using sport adapter
        print("[DEBUG] Calling select_highlights...")
        try:
            # Get user-selected highlights limit from state (None means All)
            highlights_limit = state.get('highlights_limit')
            max_highlights = highlights_limit if isinstance(highlights_limit, int) and highlights_limit > 0 else 15
            print(f"[DEBUG] User requested highlights_limit: {highlights_limit}, using max_highlights: {max_highlights}")
            
            selected_highlights = select_highlights(valid_events, sport_adapter, min_highlights=min(max_highlights, len(valid_events)), min_duration=10, max_highlights=max_highlights)
            print(f"[DEBUG] select_highlights returned {len(selected_highlights) if selected_highlights else 0} highlights")
            if not selected_highlights:
                print("[WARNING] No highlights were selected, trying with lower thresholds...")
                selected_highlights = select_highlights(valid_events, sport_adapter, min_highlights=min(5, max_highlights, len(valid_events)), min_duration=5, max_highlights=max_highlights)
                print(f"[DEBUG] Selected {len(selected_highlights)} highlights for output")
        except Exception as e:
            error_msg = f"Error during highlight selection: {str(e)}"
            print(f"[ERROR] {error_msg}")
            st.error(error_msg)
            return {"generation": error_msg, "error": str(e)}

        if not selected_highlights:
            error_msg = "No suitable highlights found in the match data."
            print(f"[ERROR] {error_msg}")
            st.error(error_msg)
            return {"generation": error_msg}
        
        # Generate clean output with exact timestamps
        print("[DEBUG] Generating highlights output...")

        # Create a structured output
        output = []
        output.append(f"# Match Highlights - {player_names}\n")
        output.append("---\n")
        output.append("## Match Introduction")
        output.append("The match begins with player introductions and preparation.\n")

        # Add each highlight with exact timestamps
        for i, event in enumerate(selected_highlights, 1):
            start_time = event.get('start_time', '00:00')
            end_time = event.get('end_time', '00:00')

            # Get sport-specific information
            sport_name = sport_adapter.sport_name.title() if sport_adapter else "Sports"
            
            # Use sport adapter to generate narrative if available
            if sport_adapter:
                narrative = sport_adapter.generate_narrative(event)
            else:
                narrative = f"{sport_name} highlight at {start_time}"

            # Add highlight with timestamp
            output.append(f"### Highlight {i} [{start_time} - {end_time}]")
            output.append(f"{narrative}\n")
    
            # Add AI reasoning if available
            ai_reason = event.get('ai_reasoning', '')
            if ai_reason and ai_reason != "AI analysis unavailable":
                ai_reason = ' '.join(ai_reason.split()[:100])  # Limit to 100 words
                output.append(f"*{ai_reason}*\n")

        # Add footer
        output.append("---\n")
        output.append(f"**Total Highlights:** {len(selected_highlights)}")

        # Join with newlines
        generation = "\n".join(output)

        # Surface a caption and validation if requested count is more than available
        requested = state.get('highlights_limit')
        effective_count = len(selected_highlights)

        # Caption for clarity
        if isinstance(requested, int) and requested > 0:
            if effective_count < requested:
                st.caption(f"Showing Top {effective_count} highlights (requested {requested})")
                st.info(f"Only {effective_count} highlights available; showing all available.")
            else:
                st.caption(f"Showing Top {requested} highlights")
        else:
            st.caption(f"Showing Top {effective_count} highlights")

        # *** KEY FIX: DISPLAY IN STREAMLIT WEB INTERFACE ***
        sport_name = sport_adapter.sport_name if sport_adapter else "Sports"
        # Get video_url from state
        video_url = state.get('video_url', '')
        
        display_success = display_highlights_in_streamlit(
            generation=generation,
            selected_highlights=selected_highlights,
            player_names=player_names,
            sport_name=sport_name,
            video_url=video_url if video_url else None
        )
        
        if not display_success:
            st.warning("There was an issue displaying the highlights, but they were generated successfully.")

        # Save files and create download packages (existing code)
        try:
            from app import PROJECT_ROOT
            output_dir = Path(PROJECT_ROOT) / 'output'
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            player_safe = "".join(c if c.isalnum() else "_" for c in player_names)
            filename = f"{player_safe}_highlights_{timestamp}.txt"
            output_file = output_dir / filename

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(generation)

            print(f"✅ TXT file saved: {output_file}")

            # Generate PDF and Audio reports
            pdf_filename = f"{player_safe}_highlights_{timestamp}.pdf"
            pdf_path = output_dir / pdf_filename
            audio_filename = f"{player_safe}_highlights_{timestamp}.mp3"
            audio_path = output_dir / audio_filename

            # Generate PDF and audio reports with selected highlights using utility modules
            try:
                from utils.pdf_generator import generate_pdf_report as generate_pdf_util
                from utils.audio_generator import generate_audio_report as generate_audio_util
                
                pdf_bytes = generate_pdf_util(
                    sport_name=sport_name,
                    player_names=player_names,
                    selected_highlights=selected_highlights,
                    generation_text=generation,
                    return_bytes=True
                )
                audio_data = generate_audio_util(
                    sport_name=sport_name.lower(),
                    player_names=player_names,
                    selected_highlights=selected_highlights,
                    generation_text=generation,
                    return_bytes=True
                )
            except ImportError:
                # Fallback if utility modules are not available
                pdf_bytes = None
                audio_data = None
                st.warning("PDF and Audio generation modules not found. Only text highlights will be available.")

            # Save PDF file
            if pdf_bytes:
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_bytes)
                print(f"✅ PDF file saved: {pdf_path}")
            else:
                pdf_path = None

            # Save audio file
            if audio_data:
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                print(f"✅ Audio file saved: {audio_path}")
            else:
                audio_path = None

            # Process video highlights if video URL is provided
            video_highlights_path = None
            video_url = state.get('video_url', '').strip()

            if video_url:
                try:
                    video_path = os.path.normpath(video_url.strip('"\''))

                    if os.path.exists(video_path) and os.access(video_path, os.R_OK):
                        st.info(f"Processing video: {os.path.basename(video_path)}")

                        # Create structured highlights data for video processing
                        structured_highlights = []

                        # Add opening segment
                        structured_highlights.append({
                            'start_time': '00:00',
                            'end_time': '03:30',
                            'description': f'{sport_name} Match Opening - {player_names}'
                        })

                        # Add actual highlights
                        for i, highlight in enumerate(selected_highlights):
                            start_time = highlight.get('start_time', '00:00')
                            end_time = highlight.get('end_time', '00:30')

                            # Get description
                            if sport_adapter:
                                raw_description = sport_adapter.generate_narrative(highlight)
                            else:
                                raw_description = f"{sport_name} highlight at {start_time}"

                            # Clean description for video captions
                            clean_desc = re.sub(r'[^\w\s.,!?\-]', ' ', str(raw_description))
                            clean_desc = ' '.join(clean_desc.split())

                            if len(clean_desc) > 200:
                                clean_desc = clean_desc[:200] + '...'

                            structured_highlights.append({
                                'start_time': start_time,
                                'end_time': end_time,
                                'description': clean_desc
                            })

                        # Generate video highlights
                        video_filename = f"{player_safe}_highlights_{timestamp}.mp4"
                        video_highlights_path = output_dir / video_filename

                        st.info("Creating video highlights with captions and transitions...")

                        try:
                            result_path = create_highlights_compilation(
                                video_path=video_path,
                                text_file_path=str(output_file),  # Use the text file we created
                                output_path=str(video_highlights_path)
                            )

                            if result_path and os.path.exists(result_path) and os.path.getsize(result_path) > 0:
                                video_highlights_path = result_path
                                st.success(f"Successfully created video highlights: {os.path.basename(video_highlights_path)}")
                            else:
                                video_highlights_path = None
                                st.error("Failed to create video highlights.")

                        except Exception as e:
                            st.error(f"Error processing video: {str(e)}")
                            video_highlights_path = None

                    else:
                        st.warning(f"Video file not found or not accessible: {video_path}")

                except Exception as e:
                    st.error(f"Error initializing video processing: {str(e)}")

            # Create download package
            st.divider()
            st.subheader("Download Your Highlights Package")
            
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                files_added = 0
                
                # Add text highlights
                if os.path.exists(output_file):
                    zipf.write(output_file, os.path.basename(output_file))
                    files_added += 1
                
                # Add audio if available
                if audio_path and os.path.exists(audio_path):
                    zipf.write(audio_path, os.path.basename(audio_path))
                    files_added += 1
                
                # Add video if available
                if video_highlights_path and os.path.exists(video_highlights_path):
                    video_size_mb = os.path.getsize(video_highlights_path) / (1024 * 1024)
                    if video_size_mb > 0:
                        zipf.write(video_highlights_path, os.path.basename(video_highlights_path))
                        files_added += 1
                
                # Add PDF if available
                if pdf_path and os.path.exists(pdf_path):
                    zipf.write(pdf_path, os.path.basename(pdf_path))
                    files_added += 1
            
            zip_bytes = zip_buffer.getvalue()
            
            # Determine package contents
            package_contents = []
            if os.path.exists(output_file):
                package_contents.append("Text")
            if audio_path and os.path.exists(audio_path):
                package_contents.append("Audio")
            if pdf_path and os.path.exists(pdf_path):
                package_contents.append("PDF")
            if video_highlights_path and os.path.exists(video_highlights_path) and os.path.getsize(video_highlights_path) > 0:
                package_contents.append("Video")
            package_contents_str = " + ".join(package_contents) if package_contents else "Text only"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="⬇️ Download Highlights Package",
                    data=zip_bytes,
                    file_name=f"Highlights_Package_{timestamp}.zip",
                    mime="application/zip",
                    key=f"download_all_{timestamp}",
                    help=f"Download a zip file containing {package_contents_str} versions of your match highlights.",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Process Another Match", use_container_width=True):
                    st.rerun()

            st.success(f"🎉 Highlights package ready! ({package_contents_str})")

        except Exception as e:
            st.warning(f"Could not save highlights files: {e}")

        # Clean up global cache
        try:
            from app import _GLOBAL_RALLY_CACHE
            _GLOBAL_RALLY_CACHE.clear()
            print("[CACHE] Global rally cache cleared after highlights generation")
        except:
            pass

        return {"generation": generation, "selected_highlights": selected_highlights}

    except Exception as e:
        error_msg = f"Error generating highlights: {str(e)}"
        print(f"[ERROR] {error_msg}")
        st.error(error_msg)
        
        # Clean up global cache even on error
        try:
            from app import _GLOBAL_RALLY_CACHE
            _GLOBAL_RALLY_CACHE.clear()
        except:
            pass
            
        return {"generation": error_msg}