"""
Audio generation utility - sport-agnostic audio report generation.
"""
import os
import datetime
from typing import List, Dict, Optional
from pathlib import Path
from .text_processing import remove_emojis, create_narrative_highlight


def generate_audio_report(
    sport_name: str,
    player_names: str, 
    selected_highlights: List[Dict] = None, 
    generation_text: str = "",
    is_summary: bool = False,
    return_bytes: bool = False,
    output_dir: Optional[str] = None
):
    """
    Generate audio report using text-to-speech with narrative highlights.
    
    Args:
        sport_name: Name of the sport (e.g., "badminton", "tennis")
        player_names: Names of the players (for filename and narration)
        selected_highlights: List of highlight dictionaries (preferred over generation text)
        generation_text: The text to convert to speech (fallback if selected_highlights not provided)
        return_bytes: If True, returns the audio as bytes instead of displaying it
        output_dir: Directory to save the audio file (optional)
        
    Returns:
        If return_bytes is True, returns the audio as bytes. Otherwise, returns the file path.
    """
    try:
        import pyttsx3
        import time
        
        # Set up output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        player_safe = "".join(c if c.isalnum() else "_" for c in player_names)
        audio_filename = f"{player_safe}_{sport_name.lower()}_highlights_{timestamp}.wav"
        audio_path = os.path.join(output_dir, audio_filename)
        
        # Generate appropriate speech content based on whether this is a summary or highlights
        clean_player_names = remove_emojis(player_names)
        
        if is_summary:
            # For summary tasks, use the generation text directly
            speech_parts = [
                f"Here is the match summary for the {sport_name} match between {clean_player_names}.",
                "",  # Empty line for better separation
                generation_text,
                "",
                f"This concludes the {sport_name} match summary between {clean_player_names}. Thank you for listening."
            ]
            speech_text = " ".join(part for part in speech_parts if part)
        else:
            # For highlights, generate narrative from rally data
            if selected_highlights and len(selected_highlights) > 0:
                speech_parts = [f"Welcome to the {sport_name} match highlights between {clean_player_names}."]
                
                # Add introduction
                speech_parts.append("Let's take a look at the key moments from the match.")
                speech_parts.append("")  # Empty line for better separation
                
                # Add narrative for each highlight
                for i, rally in enumerate(selected_highlights, 1):
                    narrative = create_narrative_highlight(rally, i, player_names, sport_name)
                    speech_parts.append(narrative)
                    
                    # Add some variety with occasional transition phrases
                    if i % 2 == 0 and i < len(selected_highlights):
                        transitions = [
                            "Moving on to the next highlight...",
                            "Let's see what happens next...",
                            "The action continues..."
                        ]
                        import random
                        speech_parts.append(random.choice(transitions))
                
                # Add closing
                speech_parts.append(f"That concludes our highlights from the {sport_name} match between {player_names}. Thank you for watching!")
                
                # Combine all parts
                speech_text = " ".join(speech_parts)
            else:
                # Fallback to original generation text if no highlights provided
                import re
                speech_text = re.sub(r'[^\w\s.,!?-]', ' ', generation_text)
                speech_text = ' '.join(speech_text.split())
        
        # Initialize text-to-speech engine
        engine = pyttsx3.init()
        
        # Set properties for better speech
        engine.setProperty('rate', 165)  # Slightly slower for clarity
        engine.setProperty('volume', 0.9)
        engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Use first available voice
        
        # Save to a temporary file with proper cleanup
        temp_path = os.path.join(output_dir, f"temp_{timestamp}.wav")
        engine.save_to_file(speech_text, str(temp_path))
        engine.runAndWait()
        
        # Properly stop the engine to release file handles
        engine.stop()
        
        # Add a small delay to ensure file is released
        time.sleep(0.5)
        
        # Read the audio data with retry mechanism
        audio_data = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(temp_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait longer between retries
                    continue
                else:
                    raise
        
        # Clean up temporary file with retry
        for attempt in range(max_retries):
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                break
            except (PermissionError, OSError):
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    # If we can't delete it, at least log it
                    print(f"Warning: Could not delete temporary file {temp_path}")
        
        if return_bytes:
            return audio_data
            
        # Save the final audio file
        with open(audio_path, "wb") as audio_file:
            audio_file.write(audio_data)
        
        return audio_path
        
    except ImportError:
        print("Error: pyttsx3 package not installed. Install with: pip install pyttsx3")
        return None
    except Exception as e:
        print(f"Error generating audio report: {e}")
        return None
