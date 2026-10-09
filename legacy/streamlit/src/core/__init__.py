"""
Core utilities for the sports analysis system.
This module contains sport-agnostic functionality.
"""

# Use absolute imports with fallback for script execution
try:
    from .validation import DataValidator, DataProcessor
except ImportError:
    # Fallback for when running as script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.validation import DataValidator, DataProcessor

__all__ = ['DataValidator', 'DataProcessor']
