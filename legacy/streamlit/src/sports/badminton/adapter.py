"""
Badminton-specific sport adapter.
This module contains all badminton-specific logic extracted from the original codebase.
"""

import datetime
import pandas as pd
from typing import Dict, List, Any, Tuple, Union
import re
import json
import concurrent.futures
import threading
from functools import partial
import time
from pathlib import Path

# Import the base adapter
try:
    from ..base import SportAdapter
except ImportError:
    # Fallback for when running as script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from sports.base import SportAdapter


class BadmintonAdapter(SportAdapter):
    """Badminton-specific implementation of the sport adapter."""

    @property
    def sport_name(self) -> str:
        return "badminton"

    def calculate_excitement_score(self, rally_data: Dict[str, Any]) -> float:
        """
        Calculate excitement score for a badminton rally based on multiple factors.
        Higher score = more exciting for highlights.
        Returns a score between 0.0 and 1.0.
        """
        score = 0.0

        try:
            # Factor 1: Rally duration (longer rallies are more exciting)
            if 'start_time' in rally_data and 'end_time' in rally_data:
                duration = self._parse_duration(rally_data['start_time'], rally_data['end_time'])
                if duration > 30:  # 30+ seconds is very exciting
                    score += 0.4
                elif duration > 15:  # 15-30 seconds is exciting
                    score += 0.2
                elif duration > 5:  # 5-15 seconds is moderately exciting
                    score += 0.1

            # Factor 2: Shot variety (more shot types = more exciting)
            if 'ball_types' in rally_data and rally_data['ball_types']:
                shot_types = set(rally_data['ball_types'].split(','))
                unique_shots = len(shot_types)
                if unique_shots > 3:
                    score += 0.3
                elif unique_shots > 2:
                    score += 0.2
                elif unique_shots > 1:
                    score += 0.1

            # Factor 3: Close score (important points are more exciting)
            if 'roundscore_A' in rally_data and 'roundscore_B' in rally_data:
                score_a = int(rally_data['roundscore_A'])
                score_b = int(rally_data['roundscore_B'])
                score_diff = abs(score_a - score_b)

                if score_diff <= 2 and max(score_a, score_b) >= 15:  # Close game late
                    score += 0.3
                elif score_diff <= 1:  # Very close
                    score += 0.2

            # Factor 4: Win reason importance
            if 'win_reason' in rally_data and rally_data['win_reason']:
                win_reason = rally_data['win_reason'].lower()
                if any(term in win_reason for term in ['smash', 'drop', 'winner', 'ace']):
                    score += 0.2
                elif any(term in win_reason for term in ['error', 'fault', 'miss']):
                    score -= 0.1  # Reduce score for unforced errors

            # Factor 5: Game phase importance
            if 'roundscore_A' in rally_data and 'roundscore_B' in rally_data:
                score_a = int(rally_data['roundscore_A'])
                score_b = int(rally_data['roundscore_B'])

                # End-game situations
                if max(score_a, score_b) >= 18:  # Late game
                    score += 0.2
                elif max(score_a, score_b) >= 15:  # Mid-late game
                    score += 0.1

            # Normalize to 0-1 range
            return min(max(score, 0.0), 1.0)

        except Exception as e:
            print(f"[WARNING] Error calculating excitement score: {e}")
            return 0.5  # Default neutral score

    def _parse_duration(self, start_time: str, end_time: str) -> float:
        """Parse duration from start and end times."""
        try:
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            return max(0, end_seconds - start_seconds)
        except:
            return 0

    def _time_to_seconds(self, time_str: str) -> float:
        """Convert MM:SS or HH:MM:SS format to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return 0
        except:
            return 0

    def generate_narrative(self, rally_data: Dict[str, Any]) -> str:
        """
        Generate a natural language narrative for a badminton rally.
        """
        try:
            start_time = rally_data.get('start_time', '00:00')
            end_time = rally_data.get('end_time', '00:00')
            winner = rally_data.get('win_point_player', 'Player')
            win_reason = rally_data.get('win_reason', 'good play')
            ball_types = rally_data.get('ball_types', '')

            # Calculate duration
            duration = self._parse_duration(start_time, end_time)

            # Build narrative
            narrative_parts = []

            # Time context
            if duration > 0:
                narrative_parts.append(f"{self._format_duration(duration)} rally")

            # Winner and action
            if winner and winner.strip():
                narrative_parts.append(f"won by {winner}")

            # Shot types
            if ball_types and ball_types.strip():
                shots = [shot.strip() for shot in ball_types.split(',') if shot.strip()]
                if shots:
                    narrative_parts.append(f"featuring {', '.join(shots[:2])}")

            # Win reason
            if win_reason and win_reason.strip():
                narrative_parts.append(f"due to {win_reason}")

            # Combine parts
            if narrative_parts:
                base_narrative = " ".join(narrative_parts)
                return f"{base_narrative} at {start_time}"
            else:
                return f"Rally at {start_time}"

        except Exception as e:
            print(f"[WARNING] Error generating narrative: {e}")
            return f"Badminton rally at {rally_data.get('start_time', '00:00')}"

    def _format_duration(self, seconds: float) -> str:
        """Format duration in natural language."""
        if seconds >= 60:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            if minutes == 1:
                return f"{minutes} minute {remaining_seconds} second"
            else:
                return f"{minutes} minutes {remaining_seconds} seconds"
        else:
            return f"{int(seconds)} seconds"

    def validate_event_data(self, event_data: Dict[str, Any]) -> bool:
        """
        Validate badminton rally data.
        """
        required_fields = ['start_time', 'end_time']

        # Check required fields
        for field in required_fields:
            if field not in event_data or not event_data[field]:
                return False

        # Validate time formats
        for time_field in ['start_time', 'end_time']:
            if not self._is_valid_time_format(event_data.get(time_field, '')):
                return False

        # Validate scores if present
        for score_field in ['roundscore_A', 'roundscore_B']:
            if score_field in event_data:
                try:
                    int(event_data[score_field])
                except (ValueError, TypeError):
                    return False

        return True

    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in valid MM:SS or HH:MM:SS format."""
        try:
            pattern = r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$'
            match = re.match(pattern, time_str.strip())
            if not match:
                return False

            minutes = int(match.group(1))
            seconds = int(match.group(2))
            hours = int(match.group(3)) if match.group(3) else 0

            # Validate ranges
            if hours > 23 or minutes > 59 or seconds > 59:
                return False

            return True
        except:
            return False

    def get_key_metrics(self, rally_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key performance metrics from badminton rally data.
        """
        metrics = {
            'duration': 0,
            'shot_variety': 0,
            'score_importance': 0,
            'game_phase': 'early',
            'excitement_score': self.calculate_excitement_score(rally_data)
        }

        try:
            # Duration
            if 'start_time' in rally_data and 'end_time' in rally_data:
                metrics['duration'] = self._parse_duration(rally_data['start_time'], rally_data['end_time'])

            # Shot variety
            if 'ball_types' in rally_data and rally_data['ball_types']:
                shots = set(rally_data['ball_types'].split(','))
                metrics['shot_variety'] = len(shots)

            # Score importance
            if 'roundscore_A' in rally_data and 'roundscore_B' in rally_data:
                score_a = int(rally_data['roundscore_A'])
                score_b = int(rally_data['roundscore_B'])
                max_score = max(score_a, score_b)

                if max_score >= 18:
                    metrics['game_phase'] = 'late'
                    metrics['score_importance'] = 1.0
                elif max_score >= 15:
                    metrics['game_phase'] = 'mid-late'
                    metrics['score_importance'] = 0.7
                elif max_score >= 10:
                    metrics['game_phase'] = 'mid'
                    metrics['score_importance'] = 0.4
                else:
                    metrics['game_phase'] = 'early'
                    metrics['score_importance'] = 0.2

        except Exception as e:
            print(f"[WARNING] Error extracting metrics: {e}")

        return metrics
