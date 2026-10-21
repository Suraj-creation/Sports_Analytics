"""
Sports module for handling different sport implementations.
This module provides a unified interface for different sports analysis.
"""

# Use absolute imports with fallback for script execution
try:
    from .base import SportAdapter, SportConfig
    from .factory import SportFactory
except ImportError:
    # Fallback for when running as script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from sports.base import SportAdapter, SportConfig
    from sports.factory import SportFactory

__all__ = ['SportAdapter', 'SportConfig', 'SportFactory']
