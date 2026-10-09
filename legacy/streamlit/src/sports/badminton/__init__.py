"""
Badminton sport module.
Contains all badminton-specific implementations.
"""

# Use absolute imports with fallback for script execution
try:
    from .adapter import BadmintonAdapter
except ImportError:
    # Fallback for when running as script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from sports.badminton.adapter import BadmintonAdapter

__all__ = ['BadmintonAdapter']
