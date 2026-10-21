"""
Factory pattern for creating sport adapters.
This module handles the creation and management of sport-specific adapters.
"""

from typing import Dict, Any, Optional
from importlib import import_module
from pathlib import Path
import json

# Import base classes with fallback
try:
    from .base import SportAdapter, SportConfig
except ImportError:
    # Fallback for when running as script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from sports.base import SportAdapter, SportConfig


class SportFactory:
    """
    Factory pattern for creating sport adapters.
    This module handles the creation and management of sport-specific adapters.
    Handles dynamic loading of sport-specific implementations.
    """

    _adapters: Dict[str, type] = {}
    _configs: Dict[str, SportConfig] = {}

    @classmethod
    def register_adapter(cls, sport_name: str, adapter_class: type):
        """Register a sport adapter class."""
        cls._adapters[sport_name.lower()] = adapter_class

    @classmethod
    def get_adapter(cls, sport_name: str) -> SportAdapter:
        """
        Get a sport adapter instance for the specified sport.
        """
        sport_name = sport_name.lower()

        # Try to get registered adapter
        if sport_name in cls._adapters:
            return cls._adapters[sport_name]()

        # Try to load dynamically
        try:
            # Import the sport module
            module = import_module(f'sports.{sport_name}.adapter')

            # Get the adapter class
            adapter_class_name = f'{sport_name.capitalize()}Adapter'
            if hasattr(module, adapter_class_name):
                adapter_class = getattr(module, adapter_class_name)
                return adapter_class()

        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported sport: {sport_name}. Error: {e}")

        raise ValueError(f"Unsupported sport: {sport_name}")

    @classmethod
    def get_available_sports(cls) -> list:
        """Get list of available sports."""
        available = []

        # Check registered adapters
        available.extend(cls._adapters.keys())

        # Check for sport directories
        sports_dir = Path(__file__).parent.parent / 'sports'
        if sports_dir.exists():
            for item in sports_dir.iterdir():
                if item.is_dir() and item.name != '__pycache__':
                    sport_name = item.name.lower()
                    # Only include badminton for now, mark others as coming soon
                    if sport_name == 'badminton':
                        if sport_name not in available:
                            available.append(sport_name)

        return sorted(available)

    @classmethod
    def get_coming_soon_sports(cls) -> list:
        """Get list of sports that are coming soon."""
        coming_soon = ['soccer', 'tennis', 'volleyball']
        return coming_soon

    @classmethod
    def get_config(cls, sport_name: str) -> Optional[SportConfig]:
        """Get configuration for a sport."""
        sport_name = sport_name.lower()

        # Try to load from cache first
        if sport_name in cls._configs:
            return cls._configs[sport_name]

        # Try to load config file
        config_path = Path(__file__).parent / f'{sport_name}.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)
                config = SportConfig(config_dict)
                cls._configs[sport_name] = config
                return config
            except Exception as e:
                print(f"[WARNING] Error loading config for {sport_name}: {e}")

        # Return default config
        config = SportConfig({
            'name': sport_name,
            'required_columns': {},
            'terminology': {},
            'game_structure': {},
            'analysis': {},
            'default_queries': [f"{sport_name} analysis"]
        })
        cls._configs[sport_name] = config
        return config

    @classmethod
    def is_sport_supported(cls, sport_name: str) -> bool:
        """Check if a sport is supported."""
        try:
            cls.get_adapter(sport_name)
            return True
        except ValueError:
            return False


# Auto-register badminton adapter
try:
    from .badminton.adapter import BadmintonAdapter
    SportFactory.register_adapter('badminton', BadmintonAdapter)
except ImportError:
    # Fallback for when running as script
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from sports.badminton.adapter import BadmintonAdapter
        SportFactory.register_adapter('badminton', BadmintonAdapter)
    except ImportError:
        pass  # Badminton adapter not available
