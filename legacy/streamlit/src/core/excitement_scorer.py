"""
Sport-agnostic excitement scoring module.
"""
import re
from typing import Dict, Any


def parse_timestamp(timestamp_str: str) -> int:
    """
    Convert timestamp string to seconds.
    Handles formats: MM:SS, MM:SS:00, HH:MM:SS
    """
    if not timestamp_str:
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


def calculate_excitement_score(rally: Dict, sport_adapter: Any) -> float:
    """
    Calculate excitement score for a rally based on multiple factors using sport configuration.
    Higher score = more exciting for highlights.
    Returns a score between 0 and 10.
    """
    print(f"[DEBUG] Calculating excitement score for rally: {rally}")
    score = 0.0
    
    try:
        # Get sport-specific configuration
        config = sport_adapter.config
        exciting_shots = getattr(config, 'exciting_shots', {})
        win_bonuses = getattr(config, 'win_bonuses', {})
        
        # If config doesn't have these attributes, try to get from analysis section
        if not exciting_shots and hasattr(config, 'analysis'):
            exciting_shots = config.analysis.get('exciting_shots', {})
        if not win_bonuses and hasattr(config, 'analysis'):
            win_bonuses = config.analysis.get('win_bonuses', {})
        
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
            max_score = getattr(config.game_structure, 'max_score', 21) if hasattr(config, 'game_structure') else 21
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
