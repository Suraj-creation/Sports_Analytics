"""
Base classes and interfaces for sport-specific adapters.
This module defines the contracts that all sport adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class SportConfig:
    """Configuration class for sport-specific settings."""

    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict

    @property
    def name(self) -> str:
        return self._config.get('name', 'unknown')

    @property
    def required_columns(self) -> Dict[str, str]:
        return self._config.get('required_columns', {})

    @property
    def terminology(self) -> Dict[str, str]:
        return self._config.get('terminology', {})

    @property
    def game_structure(self) -> Dict[str, Any]:
        return self._config.get('game_structure', {})

    @property
    def analysis(self) -> Dict[str, Any]:
        return self._config.get('analysis', {})

    @property
    def default_queries(self) -> List[str]:
        return self._config.get('default_queries', [f"{self.name} analysis"])

    def get_terminology(self, key: str, default: str = None) -> str:
        """Get sport-specific terminology."""
        return self.terminology.get(key, default or key)

    @property
    def placeholders(self) -> Dict[str, str]:
        return self._config.get('ui_elements', {}).get('placeholders', {})


class SportAdapter(ABC):
    """
    Abstract base class for sport-specific adapters.
    All sports must implement these methods to work with the system.
    """

    def __init__(self):
        self._config = self._load_config()

    @property
    @abstractmethod
    def sport_name(self) -> str:
        """Return the name of the sport this adapter handles."""
        pass

    @property
    def config(self) -> SportConfig:
        """Return the sport configuration."""
        return self._config

    def _load_config(self) -> SportConfig:
        """Load configuration from file."""
        config_path = Path(__file__).parent.parent / 'config' / f'{self.sport_name}.json'
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                return SportConfig(json.load(f))
        else:
            # Return default config
            return SportConfig({
                'name': self.sport_name,
                'required_columns': {},
                'terminology': {},
                'game_structure': {},
                'analysis': {},
                'default_queries': [f"{self.sport_name} analysis"]
            })

    @abstractmethod
    def calculate_excitement_score(self, event_data: Dict[str, Any]) -> float:
        """
        Calculate how exciting this event is for highlight generation.
        Returns a score between 0.0 and 1.0 (1.0 being most exciting).
        """
        pass

    @abstractmethod
    def generate_narrative(self, event_data: Dict[str, Any]) -> str:
        """
        Generate a natural language description of the event.
        Used for highlights and summaries.
        """
        pass

    @abstractmethod
    def validate_event_data(self, event_data: Dict[str, Any]) -> bool:
        """
        Validate that the event data is valid for this sport.
        Returns True if valid, False otherwise.
        """
        pass

    @abstractmethod
    def get_key_metrics(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key performance metrics from event data.
        Used for summarization and analysis.
        """
        pass

    def get_default_queries(self) -> List[str]:
        """Get default search queries for this sport."""
        return self.config.default_queries
