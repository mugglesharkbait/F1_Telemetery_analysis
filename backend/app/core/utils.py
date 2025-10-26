"""
Utility functions for F1 data processing and formatting
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Optional, Any
import fastf1


def format_timedelta(td: Optional[pd.Timedelta]) -> Optional[str]:
    """
    Format pandas Timedelta to readable string format (MM:SS.mmm)

    Args:
        td: Pandas Timedelta object

    Returns:
        Formatted string or None if td is None/NaT
    """
    if td is None or pd.isna(td):
        return None

    total_seconds = td.total_seconds()
    if total_seconds < 0:
        return None

    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    return f"{minutes}:{seconds:06.3f}"


def timedelta_to_seconds(td: Optional[pd.Timedelta]) -> Optional[float]:
    """
    Convert pandas Timedelta to seconds

    Args:
        td: Pandas Timedelta object

    Returns:
        Seconds as float or None
    """
    if td is None or pd.isna(td):
        return None
    return td.total_seconds()


def safe_get(data: Any, key: str, default: Any = None) -> Any:
    """
    Safely get value from dict-like object or pandas Series

    Args:
        data: Data object to extract from
        key: Key to extract
        default: Default value if key not found or value is NaN

    Returns:
        Value or default
    """
    try:
        if isinstance(data, pd.Series):
            value = data.get(key, default)
        else:
            value = data[key]

        # Check for NaN/NaT
        if pd.isna(value):
            return default

        return value
    except (KeyError, IndexError, TypeError):
        return default


def get_team_color(team_name: str) -> str:
    """
    Get team color from FastF1 plotting module

    Args:
        team_name: Name of the team

    Returns:
        Hex color string
    """
    try:
        from fastf1.plotting import team_color
        color = team_color(team_name)
        return color if color else "#CCCCCC"
    except Exception:
        return "#CCCCCC"


def interpolate_telemetry(telemetry: pd.DataFrame, distance_points: int = 1000) -> tuple:
    """
    Interpolate telemetry data onto a common distance axis

    Args:
        telemetry: Telemetry DataFrame with Distance column
        distance_points: Number of interpolation points

    Returns:
        Tuple of (distance_axis, interpolated_data_dict)
    """
    if telemetry.empty or 'Distance' not in telemetry.columns:
        return np.array([]), {}

    max_distance = telemetry['Distance'].max()
    distance_axis = np.linspace(0, max_distance, distance_points)

    interpolated = {}

    # Speed
    if 'Speed' in telemetry.columns:
        interpolated['speed'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['Speed']
        ).tolist()

    # RPM
    if 'RPM' in telemetry.columns:
        interpolated['rpm'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['RPM']
        ).tolist()

    # Gear
    if 'nGear' in telemetry.columns:
        interpolated['n_gear'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['nGear']
        ).astype(int).tolist()

    # Throttle
    if 'Throttle' in telemetry.columns:
        interpolated['throttle'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['Throttle']
        ).tolist()

    # Brake (binary, so round after interpolation)
    if 'Brake' in telemetry.columns:
        brake_interp = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['Brake'].astype(int)
        )
        interpolated['brake'] = (brake_interp > 0.5).tolist()

    # DRS
    if 'DRS' in telemetry.columns:
        interpolated['drs'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['DRS']
        ).astype(int).tolist()

    # Time
    if 'Time' in telemetry.columns:
        time_seconds = telemetry['Time'].dt.total_seconds()
        interpolated['time'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            time_seconds
        ).tolist()

    # SessionTime
    if 'SessionTime' in telemetry.columns:
        session_time_seconds = telemetry['SessionTime'].dt.total_seconds()
        interpolated['session_time'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            session_time_seconds
        ).tolist()

    # Position coordinates
    if 'X' in telemetry.columns:
        interpolated['x'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['X']
        ).tolist()

    if 'Y' in telemetry.columns:
        interpolated['y'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['Y']
        ).tolist()

    if 'Z' in telemetry.columns:
        interpolated['z'] = np.interp(
            distance_axis,
            telemetry['Distance'],
            telemetry['Z']
        ).tolist()

    return distance_axis.tolist(), interpolated


def calculate_delta_time(tel1: pd.DataFrame, tel2: pd.DataFrame, distance_axis: np.ndarray) -> list:
    """
    Calculate time delta between two telemetry datasets

    Args:
        tel1: First telemetry DataFrame
        tel2: Second telemetry DataFrame
        distance_axis: Common distance axis

    Returns:
        List of delta times (positive means tel2 is slower)
    """
    if tel1.empty or tel2.empty:
        return [0.0] * len(distance_axis)

    # Interpolate times
    time1 = np.interp(
        distance_axis,
        tel1['Distance'],
        tel1['Time'].dt.total_seconds()
    )

    time2 = np.interp(
        distance_axis,
        tel2['Distance'],
        tel2['Time'].dt.total_seconds()
    )

    # Delta = time2 - time1 (positive means driver2 is slower at this point)
    delta = time2 - time1

    return delta.tolist()


def get_compound_colors() -> dict:
    """
    Get tire compound colors from FastF1

    Returns:
        Dictionary mapping compound names to hex colors
    """
    try:
        from fastf1.plotting import COMPOUND_COLORS
        return {
            'SOFT': COMPOUND_COLORS.get('SOFT', '#FF3333'),
            'MEDIUM': COMPOUND_COLORS.get('MEDIUM', '#FFF200'),
            'HARD': COMPOUND_COLORS.get('HARD', '#EBEBEB'),
            'INTERMEDIATE': COMPOUND_COLORS.get('INTERMEDIATE', '#43B02A'),
            'WET': COMPOUND_COLORS.get('WET', '#0067AD'),
            'UNKNOWN': COMPOUND_COLORS.get('UNKNOWN', '#CCCCCC'),
            'TEST_UNKNOWN': COMPOUND_COLORS.get('TEST_UNKNOWN', '#434343'),
        }
    except Exception:
        # Fallback colors
        return {
            'SOFT': '#FF3333',
            'MEDIUM': '#FFF200',
            'HARD': '#EBEBEB',
            'INTERMEDIATE': '#43B02A',
            'WET': '#0067AD',
            'UNKNOWN': '#CCCCCC',
        }


def clean_dataframe_for_json(df: pd.DataFrame) -> list:
    """
    Clean pandas DataFrame for JSON serialization
    Convert timestamps and NaN values

    Args:
        df: DataFrame to clean

    Returns:
        List of dictionaries ready for JSON
    """
    # Replace NaN with None
    df = df.replace({pd.NaT: None, np.nan: None})

    # Convert to dict
    records = df.to_dict('records')

    # Clean each record
    cleaned = []
    for record in records:
        clean_record = {}
        for key, value in record.items():
            # Convert timestamps
            if isinstance(value, (pd.Timestamp, pd.Timedelta)):
                if pd.isna(value):
                    clean_record[key] = None
                elif isinstance(value, pd.Timedelta):
                    clean_record[key] = value.total_seconds()
                else:
                    clean_record[key] = value.isoformat()
            # Convert numpy types
            elif isinstance(value, (np.integer, np.floating)):
                clean_record[key] = value.item()
            else:
                clean_record[key] = value
        cleaned.append(clean_record)

    return cleaned


def validate_session_type(session_type: str) -> str:
    """
    Validate and normalize session type

    Args:
        session_type: Session type string

    Returns:
        Normalized session type

    Raises:
        ValueError if invalid session type
    """
    valid_types = {
        'FP1': 'FP1', 'fp1': 'FP1', '1': 'FP1', 'practice1': 'FP1',
        'FP2': 'FP2', 'fp2': 'FP2', '2': 'FP2', 'practice2': 'FP2',
        'FP3': 'FP3', 'fp3': 'FP3', '3': 'FP3', 'practice3': 'FP3',
        'Q': 'Q', 'q': 'Q', 'qualifying': 'Q', '4': 'Q',
        'S': 'S', 's': 'S', 'sprint': 'S',
        'SS': 'SS', 'ss': 'SS', 'sprint_shootout': 'SS',
        'SQ': 'SQ', 'sq': 'SQ', 'sprint_qualifying': 'SQ',
        'R': 'R', 'r': 'R', 'race': 'R', '5': 'R',
    }

    normalized = valid_types.get(session_type)
    if not normalized:
        raise ValueError(
            f"Invalid session type: {session_type}. "
            f"Valid types: FP1, FP2, FP3, Q, S, SS, SQ, R"
        )

    return normalized
