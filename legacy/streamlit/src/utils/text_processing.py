"""
Text processing utilities - sport-agnostic text manipulation functions.
"""
import re
from typing import Dict, List


def remove_emojis(text: str) -> str:
    """Remove emojis and other special characters from text."""
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


def create_narrative_highlight(rally: Dict, index: int, player_names: str = "the players", sport_name: str = "match") -> str:
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
        f"At {natural_start} into the {sport_name}, {win_player} takes the lead with an impressive sequence of {shot_desc} to win the point.",
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
