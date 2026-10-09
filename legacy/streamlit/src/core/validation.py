"""
Data validation and processing utilities.
This module handles data validation and processing for different sports.
"""

import pandas as pd
import csv
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Use absolute import instead of relative import
try:
    from sports.base import SportAdapter
except ImportError:
    # Fallback for when running as script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from sports.base import SportAdapter


class DataValidator:
    """Handles validation of sport-specific data."""

    def __init__(self, sport_adapter: SportAdapter):
        self.adapter = sport_adapter

    def validate_csv_files(self, path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Validate and parse CSV files from a path.
        Accepts both directory path or single file path.
        Returns (valid_files, rally_data).
        """
        if os.path.isfile(path):
            # Handle single file
            if not path.lower().endswith('.csv'):
                raise ValueError("File is not a CSV file")
            file_data = self._validate_csv_file(path)
            return [os.path.basename(path)], file_data

        elif os.path.isdir(path):
            # Handle directory
            csv_files = [f for f in os.listdir(path)
                        if os.path.isfile(os.path.join(path, f))
                        and f.lower().endswith('.csv')]

            if not csv_files:
                raise ValueError("No CSV files found in directory")

            valid_files = []
            all_rally_data = []

            for filename in csv_files:
                file_path = os.path.join(path, filename)
                try:
                    file_data = self._validate_csv_file(file_path)
                    if file_data:
                        valid_files.append(filename)
                        all_rally_data.extend(file_data)
                except Exception as e:
                    print(f"[WARNING] Error processing {filename}: {e}")
                    continue

            return valid_files, all_rally_data

        else:
            raise ValueError("Path is invalid - not a file or directory")

    def _validate_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Validate and parse a single CSV file."""
        try:
            # Read the CSV file
            with open(file_path, 'r', encoding='utf-8') as f:
                # Check if file is empty
                first_line = f.readline().strip()
                if not first_line:
                    raise ValueError("File is empty")

                # Read the rest of the file
                content = first_line + '\n' + f.read()

            # Parse the CSV content
            csv_reader = csv.DictReader(content.splitlines())

            if not csv_reader.fieldnames:
                raise ValueError("No headers found")

            # Check for required columns
            required_columns = set(self.adapter.config.required_columns.keys())
            available_columns = set(csv_reader.fieldnames or [])

            missing_columns = required_columns - available_columns
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Process each row
            rally_data = []
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Validate the row data
                    validated_row = self._validate_row_data(row)
                    if validated_row:
                        # Add metadata
                        validated_row['_source_file'] = os.path.basename(file_path)
                        validated_row['_row_number'] = row_num
                        rally_data.append(validated_row)
                except Exception as e:
                    print(f"[WARNING] Error processing row {row_num} in {file_path}: {e}")
                    continue

            return rally_data

        except Exception as e:
            raise ValueError(f"Error processing CSV file {file_path}: {e}")

    def _validate_row_data(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Validate individual row data."""
        try:
            # Clean the row data
            cleaned_row = {}
            for key, value in row.items():
                if key is not None:
                    cleaned_key = key.strip()
                    cleaned_value = value.strip() if value else ''
                    cleaned_row[cleaned_key] = cleaned_value

            # Use sport adapter to validate
            if self.adapter.validate_event_data(cleaned_row):
                return cleaned_row
            else:
                return None

        except Exception as e:
            print(f"[WARNING] Error validating row: {e}")
            return None

    def validate_data_structure(self, data: List[Dict[str, Any]]) -> bool:
        """Validate the overall structure of parsed data."""
        if not isinstance(data, list) or not data:
            return False

        # Check if all items are dictionaries
        if not all(isinstance(item, dict) for item in data):
            return False

        # Check if at least one item has the required fields
        if not data:
            return False

        sample_item = data[0]
        required_columns = set(self.adapter.config.required_columns.keys())

        # Check if sample has required fields
        sample_fields = set(sample_item.keys())
        if not required_columns.issubset(sample_fields):
            return False

        return True


class DataProcessor:
    """Handles processing of validated data."""

    def __init__(self, sport_adapter: SportAdapter):
        self.adapter = sport_adapter

    def process_rally_data(self, rally_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enrich rally data."""
        processed_data = []

        for rally in rally_data:
            try:
                # Create enriched rally data
                enriched_rally = rally.copy()

                # Add computed metrics
                metrics = self.adapter.get_key_metrics(rally)
                enriched_rally.update({
                    'computed_metrics': metrics,
                    'excitement_score': metrics.get('excitement_score', 0.5),
                    'sport': self.adapter.sport_name
                })

                # Generate narrative
                enriched_rally['narrative'] = self.adapter.generate_narrative(rally)

                processed_data.append(enriched_rally)

            except Exception as e:
                print(f"[WARNING] Error processing rally: {e}")
                continue

        return processed_data

    def filter_highlights(self, processed_data: List[Dict[str, Any]],
                         min_score: float = 0.6,
                         max_highlights: int = 10) -> List[Dict[str, Any]]:
        """Filter data for highlight-worthy events."""
        # Sort by excitement score
        sorted_data = sorted(processed_data,
                           key=lambda x: x.get('excitement_score', 0),
                           reverse=True)

        # Filter by minimum score
        filtered = [item for item in sorted_data
                   if item.get('excitement_score', 0) >= min_score]

        # Limit number of highlights
        return filtered[:max_highlights]

    def generate_summary_stats(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the dataset."""
        if not processed_data:
            return {}

        # Calculate basic stats
        total_rallies = len(processed_data)
        avg_excitement = sum(item.get('excitement_score', 0) for item in processed_data) / total_rallies

        # Calculate duration stats
        durations = []
        for item in processed_data:
            metrics = item.get('computed_metrics', {})
            duration = metrics.get('duration', 0)
            if duration > 0:
                durations.append(duration)

        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        # Calculate score distribution
        excitement_distribution = {
            'high': len([x for x in processed_data if x.get('excitement_score', 0) >= 0.8]),
            'medium': len([x for x in processed_data if 0.5 <= x.get('excitement_score', 0) < 0.8]),
            'low': len([x for x in processed_data if x.get('excitement_score', 0) < 0.5])
        }

        return {
            'total_rallies': total_rallies,
            'average_excitement_score': avg_excitement,
            'average_duration': avg_duration,
            'max_duration': max_duration,
            'excitement_distribution': excitement_distribution,
            'sport': self.adapter.sport_name
        }
