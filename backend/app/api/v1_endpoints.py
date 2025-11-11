"""
F1 Telemetry API - Phase 1 MVP Endpoints
Implements 11 core endpoints for the telemetry dashboard
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional
import fastf1
import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path

from app.models.schemas import (
    # Events & Schedule
    SeasonsResponse,
    EventsResponse,
    RaceEventInfo,
    SessionsResponse,
    SessionInfo,
    # Drivers
    DriversResponse,
    DriverInfo,
    # Session Results
    SessionResultsResponse,
    DriverResult,
    # Laps
    LapsResponse,
    LapData,
    # Telemetry
    ComparisonTelemetry,
    LapInfo,
    # Circuit
    CircuitInfo,
    CornerAnnotation,
    TrackMapData,
    # Weather
    WeatherResponse,
    WeatherDataPoint,
    WeatherSummary,
    # Visualization
    TeamColorsResponse,
    TeamColor,
    CompoundColorsResponse,
    CompoundColor,
)
from app.core import (
    format_timedelta,
    timedelta_to_seconds,
    safe_get,
    interpolate_telemetry,
    calculate_delta_time,
    get_compound_colors,
    validate_session_type,
    settings,
)

router = APIRouter()

# Enable FastF1 cache - create directory if it doesn't exist
if settings.FASTF1_CACHE_ENABLED:
    cache_dir = Path(settings.FASTF1_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))

# Cache for seasons data (computed once)
_cached_seasons: Optional[List[int]] = None

# Cache for drivers data to avoid repeated session loads
_drivers_cache: dict = {}

# Cache for session objects to avoid repeated loads (MAJOR PERFORMANCE IMPROVEMENT)
# Key format: "{year}_{event}_{session_type}_{load_signature}"
_session_cache: dict = {}
_session_cache_max_size = 20  # Keep last 20 sessions in memory


def get_cached_session(year: int, event: str, session_type: str, **load_params):
    """
    Get a cached session object or load it fresh if not in cache.
    This dramatically improves performance by avoiding repeated session loads.

    Args:
        year: Season year
        event: Event identifier
        session_type: Session type (already normalized)
        **load_params: Parameters for session.load() (e.g., telemetry=True, laps=True)

    Returns:
        Loaded FastF1 session object
    """
    # Create cache key including load parameters
    load_sig = "_".join(f"{k}={v}" for k, v in sorted(load_params.items()))
    cache_key = f"{year}_{event}_{session_type}_{load_sig}"

    # Return cached session if available
    if cache_key in _session_cache:
        return _session_cache[cache_key]

    # Load fresh session
    session = fastf1.get_session(year, event, session_type)
    session.load(**load_params)

    # Maintain cache size limit (FIFO eviction)
    if len(_session_cache) >= _session_cache_max_size:
        # Remove oldest entry
        oldest_key = next(iter(_session_cache))
        del _session_cache[oldest_key]

    # Cache the loaded session
    _session_cache[cache_key] = session
    return session


# ============================================================================
# 1. EVENT & SCHEDULE DISCOVERY (4 endpoints)
# ============================================================================

@router.get("/seasons", response_model=SeasonsResponse, tags=["Events"])
async def get_seasons():
    """
    Get list of available F1 seasons

    Returns all years where FastF1 has data available
    Note: Data quality and completeness varies by year
    - 2018+: Full telemetry and timing data
    - 2011-2017: Partial data (some sessions may be incomplete)
    - Before 2011: Limited data availability
    """
    global _cached_seasons

    if _cached_seasons is not None:
        return SeasonsResponse(seasons=_cached_seasons)

    def _get_seasons():
        seasons = []
        current_year = datetime.now().year
        # Try all years from 1950 (first F1 season) to present
        # FastF1 will return data for years where it's available
        for year in range(1950, current_year + 1):
            try:
                schedule = fastf1.get_event_schedule(year)
                if not schedule.empty:
                    seasons.append(year)
            except Exception:
                # Year not available in FastF1
                pass
        return sorted(seasons, reverse=True)

    try:
        seasons = await run_in_threadpool(_get_seasons)
        _cached_seasons = seasons
        return SeasonsResponse(seasons=seasons)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching seasons: {str(e)}")


@router.get("/events/{year}", response_model=EventsResponse, tags=["Events"])
async def get_events(year: int):
    """
    Get all race events for a specific season

    Args:
        year: Season year (e.g., 2024)

    Returns:
        List of race events with dates and locations
    """
    def _get_events():
        schedule = fastf1.get_event_schedule(year)
        events = []

        for _, event_data in schedule.iterrows():
            # Determine event format based on session availability
            event_format = "conventional"
            if safe_get(event_data, 'EventFormat'):
                event_format = safe_get(event_data, 'EventFormat', 'conventional')

            events.append(RaceEventInfo(
                round_number=int(safe_get(event_data, 'RoundNumber', 0)),
                event_name=safe_get(event_data, 'EventName', 'Unknown'),
                official_event_name=safe_get(event_data, 'OfficialEventName'),
                location=safe_get(event_data, 'Location', 'Unknown'),
                country=safe_get(event_data, 'Country', 'Unknown'),
                country_code=safe_get(event_data, 'Country'),
                event_date=safe_get(event_data, 'EventDate'),
                event_format=event_format,
                is_testing=safe_get(event_data, 'EventName', '').lower().find('test') >= 0
            ))

        return events

    try:
        events = await run_in_threadpool(_get_events)
        return EventsResponse(events=events)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Events for year {year} not found: {str(e)}"
        )


@router.get("/events/{year}/{event_identifier}/sessions", response_model=SessionsResponse, tags=["Events"])
async def get_sessions(year: int, event_identifier: str):
    """
    Get all sessions for a specific event

    Args:
        year: Season year
        event_identifier: Event name, location, or round number

    Returns:
        List of sessions (Practice, Qualifying, Sprint, Race)
    """
    def _get_sessions():
        event = fastf1.get_event(year, event_identifier)
        sessions = []

        # Standard F1 sessions in order
        session_types = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R']
        session_names_map = {
            'FP1': 'Practice 1',
            'FP2': 'Practice 2',
            'FP3': 'Practice 3',
            'Q': 'Qualifying',
            'S': 'Sprint',
            'SS': 'Sprint Shootout',
            'SQ': 'Sprint Qualifying',
            'R': 'Race'
        }

        # Try to get sessions from event
        for i, session_type in enumerate(session_types, 1):
            try:
                session_obj = fastf1.get_session(year, event_identifier, session_type)
                if session_obj is not None:
                    sessions.append(SessionInfo(
                        session_name=session_names_map.get(session_type, session_type),
                        session_type=session_type,
                        session_number=i,
                        date_utc=session_obj.date if hasattr(session_obj, 'date') else datetime.now()
                    ))
            except Exception:
                # Session doesn't exist for this event (e.g., no Sprint at some races)
                pass

        return sessions

    try:
        sessions = await run_in_threadpool(_get_sessions)
        return SessionsResponse(sessions=sessions)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Sessions for {event_identifier} in {year} not found: {str(e)}"
        )


@router.get("/sessions/{year}/{event}/{session_type}/drivers", response_model=DriversResponse, tags=["Drivers"])
async def get_drivers(year: int, event: str, session_type: str):
    """
    Get all drivers participating in a session

    Args:
        year: Season year
        event: Event identifier
        session_type: Session type (FP1, FP2, FP3, Q, S, SS, SQ, R)

    Returns:
        List of drivers with team information and colors
    """
    def _get_drivers():
        # Validate and normalize session type
        normalized_session = validate_session_type(session_type)

        # Create cache key
        cache_key = f"{year}_{event}_{normalized_session}"

        # Return from cache if available
        if cache_key in _drivers_cache:
            return _drivers_cache[cache_key]

        session = fastf1.get_session(year, event, normalized_session)

        # Load only results data - this is faster than loading everything
        # Use laps=False, telemetry=False, weather=False to minimize data
        session.load(laps=False, telemetry=False, weather=False)

        drivers = []
        results = session.results

        if results is not None and not results.empty:
            for _, driver_data in results.iterrows():
                driver_num = safe_get(driver_data, 'DriverNumber', 'UNK')
                abbr = safe_get(driver_data, 'Abbreviation', 'UNK')
                full_name = safe_get(driver_data, 'FullName', 'Unknown Driver')
                first_name = safe_get(driver_data, 'FirstName', '')
                last_name = safe_get(driver_data, 'LastName', '')
                team_name = safe_get(driver_data, 'TeamName', 'Unknown Team')
                team_color = safe_get(driver_data, 'TeamColor', '#CCCCCC')
                country_code = safe_get(driver_data, 'CountryCode', '')

                drivers.append(DriverInfo(
                    driver_number=str(driver_num),
                    abbreviation=abbr,
                    full_name=full_name,
                    first_name=first_name,
                    last_name=last_name,
                    team_name=team_name,
                    team_color=f"#{team_color}" if not team_color.startswith('#') else team_color,
                    country_code=country_code
                ))

        # Cache the result
        _drivers_cache[cache_key] = drivers
        return drivers

    try:
        drivers = await run_in_threadpool(_get_drivers)
        return DriversResponse(drivers=drivers)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Drivers for {event} {session_type} in {year} not found: {str(e)}"
        )


# ============================================================================
# 2. SESSION RESULTS (1 endpoint)
# ============================================================================

@router.get("/sessions/{year}/{event}/{session_type}/results", response_model=SessionResultsResponse, tags=["Results"])
async def get_session_results(year: int, event: str, session_type: str):
    """
    Get complete session results with driver standings

    Args:
        year: Season year
        event: Event identifier
        session_type: Session type

    Returns:
        Session results with all driver classifications
    """
    def _get_results():
        normalized_session = validate_session_type(session_type)

        # Use cached session with selective loading - only need results, not telemetry/laps
        session = get_cached_session(
            year, event, normalized_session,
            laps=False, telemetry=False, weather=False, messages=False
        )

        results_data = []
        results_df = session.results

        if results_df is not None and not results_df.empty:
            for _, driver in results_df.iterrows():
                # Format qualifying times
                q1 = format_timedelta(safe_get(driver, 'Q1'))
                q2 = format_timedelta(safe_get(driver, 'Q2'))
                q3 = format_timedelta(safe_get(driver, 'Q3'))

                # Format race time
                race_time = format_timedelta(safe_get(driver, 'Time'))

                team_color = safe_get(driver, 'TeamColor', 'CCCCCC')
                if not team_color.startswith('#'):
                    team_color = f"#{team_color}"

                results_data.append(DriverResult(
                    position=safe_get(driver, 'Position'),
                    driver_number=str(safe_get(driver, 'DriverNumber', 'UNK')),
                    broadcast_name=safe_get(driver, 'BroadcastName', ''),
                    full_name=safe_get(driver, 'FullName', 'Unknown'),
                    abbreviation=safe_get(driver, 'Abbreviation', 'UNK'),
                    driver_id=safe_get(driver, 'DriverId', ''),
                    team_name=safe_get(driver, 'TeamName', 'Unknown'),
                    team_color=team_color,
                    team_id=safe_get(driver, 'TeamId', ''),
                    first_name=safe_get(driver, 'FirstName', ''),
                    last_name=safe_get(driver, 'LastName', ''),
                    country_code=safe_get(driver, 'CountryCode'),
                    grid_position=safe_get(driver, 'GridPosition'),
                    classified_position=str(safe_get(driver, 'ClassifiedPosition', '')),
                    q1=q1,
                    q2=q2,
                    q3=q3,
                    time=race_time,
                    status=safe_get(driver, 'Status'),
                    points=float(safe_get(driver, 'Points', 0.0)),
                    laps=safe_get(driver, 'Laps')
                ))

        return SessionResultsResponse(
            session_info={
                "year": year,
                "event": event,
                "session_type": normalized_session,
                "session_name": session.name if hasattr(session, 'name') else normalized_session
            },
            results=results_data
        )

    try:
        return await run_in_threadpool(_get_results)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Results for {event} {session_type} in {year} not found: {str(e)}"
        )


# ============================================================================
# 3. LAP TIMING (1 endpoint)
# ============================================================================

@router.get("/sessions/{year}/{event}/{session_type}/laps", response_model=LapsResponse, tags=["Laps"])
async def get_laps(
    year: int,
    event: str,
    session_type: str,
    driver: Optional[str] = Query(None, description="Filter by driver abbreviation"),
    quicklaps_only: bool = Query(False, description="Only laps within 107% of fastest"),
    exclude_deleted: bool = Query(True, description="Exclude deleted laps"),
    limit: Optional[int] = Query(None, description="Limit number of laps returned")
):
    """
    Get lap timing data for a session

    Args:
        year: Season year
        event: Event identifier
        session_type: Session type
        driver: Optional driver filter
        quicklaps_only: Filter to only quick laps
        exclude_deleted: Exclude deleted laps
        limit: Maximum number of laps to return

    Returns:
        List of lap data with timing and tire information
    """
    def _get_laps():
        normalized_session = validate_session_type(session_type)

        # Use cached session with selective loading - only need laps data
        session = get_cached_session(
            year, event, normalized_session,
            laps=True, telemetry=False, weather=False, messages=False
        )

        laps_df = session.laps

        # Apply filters
        if driver:
            laps_df = laps_df.pick_drivers(driver)

        if quicklaps_only:
            laps_df = laps_df.pick_quicklaps()

        if exclude_deleted:
            laps_df = laps_df.pick_not_deleted()

        # Limit results
        if limit and limit > 0:
            laps_df = laps_df.head(limit)

        # Convert to response format
        laps_data = []
        for _, lap in laps_df.iterlaps():
            laps_data.append(LapData(
                time=format_timedelta(safe_get(lap, 'Time')) or "0:00.000",
                driver=safe_get(lap, 'Driver', 'UNK'),
                driver_number=str(safe_get(lap, 'DriverNumber', 'UNK')),
                lap_time=format_timedelta(safe_get(lap, 'LapTime')),
                lap_time_seconds=timedelta_to_seconds(safe_get(lap, 'LapTime')),
                lap_number=float(safe_get(lap, 'LapNumber', 0)),
                lap_start_time=format_timedelta(safe_get(lap, 'LapStartTime')),
                stint=safe_get(lap, 'Stint'),
                sector_1_time=format_timedelta(safe_get(lap, 'Sector1Time')),
                sector_2_time=format_timedelta(safe_get(lap, 'Sector2Time')),
                sector_3_time=format_timedelta(safe_get(lap, 'Sector3Time')),
                speed_i1=safe_get(lap, 'SpeedI1'),
                speed_i2=safe_get(lap, 'SpeedI2'),
                speed_fl=safe_get(lap, 'SpeedFL'),
                speed_st=safe_get(lap, 'SpeedST'),
                is_personal_best=bool(safe_get(lap, 'IsPersonalBest', False)),
                is_accurate=bool(safe_get(lap, 'IsAccurate', True)),
                compound=safe_get(lap, 'Compound', 'UNKNOWN'),
                tyre_life=safe_get(lap, 'TyreLife'),
                fresh_tyre=safe_get(lap, 'FreshTyre'),
                pit_out_time=format_timedelta(safe_get(lap, 'PitOutTime')),
                pit_in_time=format_timedelta(safe_get(lap, 'PitInTime')),
                team=safe_get(lap, 'Team'),
                track_status=str(safe_get(lap, 'TrackStatus', '1')),
                position=safe_get(lap, 'Position'),
                deleted=safe_get(lap, 'Deleted'),
                deleted_reason=safe_get(lap, 'DeletedReason', '')
            ))

        return LapsResponse(
            laps=laps_data,
            total_laps=len(laps_data)
        )

    try:
        return await run_in_threadpool(_get_laps)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Laps for {event} {session_type} in {year} not found: {str(e)}"
        )


# ============================================================================
# 4. TELEMETRY COMPARISON (1 endpoint - CORE FEATURE)
# ============================================================================

@router.get("/telemetry/compare", response_model=ComparisonTelemetry, tags=["Telemetry"])
async def compare_telemetry(
    year: int = Query(..., description="Season year"),
    event: str = Query(..., description="Event identifier"),
    session_type: str = Query(..., description="Session type"),
    driver1: str = Query(..., description="First driver (abbreviation like 'VER' or number like '1')"),
    driver2: str = Query(..., description="Second driver (abbreviation like 'PIA' or number like '81')"),
    lap1: Optional[int] = Query(None, description="Lap number for driver1 (default: fastest)"),
    lap2: Optional[int] = Query(None, description="Lap number for driver2 (default: fastest)")
):
    """
    **CORE ENDPOINT**: Compare telemetry between two drivers

    This is the primary endpoint for the telemetry comparison dashboard.
    Returns detailed telemetry data interpolated onto a common distance axis.

    Args:
        year: Season year
        event: Event identifier
        session_type: Session type
        driver1: First driver (abbreviation or driver number)
        driver2: Second driver (abbreviation or driver number)
        lap1: Specific lap for driver1 (optional)
        lap2: Specific lap for driver2 (optional)

    Returns:
        Detailed telemetry comparison with speed, throttle, brake, gear, and delta time
    """
    def _compare_telemetry():
        normalized_session = validate_session_type(session_type)

        # Check if this year likely has telemetry based on year
        # Proactively reject years that definitely don't have telemetry
        if year < 2011:
            raise ValueError(
                f"Telemetry data is not available for {year}. "
                f"Telemetry data is only available from 2011 onwards. "
                f"For complete telemetry data, please use years 2018-2025."
            )

        # Load session with caching (MAJOR PERFORMANCE IMPROVEMENT)
        # Use selective loading - only telemetry, laps, and results (not weather/messages/car data)
        try:
            session = get_cached_session(
                year, event, normalized_session,
                telemetry=True, laps=True, weather=False, messages=False
            )
        except Exception as e:
            error_msg = str(e)
            # Handle cases where telemetry loading fails
            if "not been loaded" in error_msg or "no data" in error_msg.lower() or "DataNotLoadedError" in error_msg:
                raise ValueError(
                    f"Telemetry data is not available for this session ({event} {year} {normalized_session}). "
                    f"This session may not have telemetry data. "
                    f"For guaranteed telemetry data, please use years 2018-2025."
                )
            else:
                # Re-raise unexpected errors
                raise

        # Get laps for both drivers
        driver1_laps = session.laps.pick_drivers(driver1)
        driver2_laps = session.laps.pick_drivers(driver2)

        if driver1_laps.empty:
            raise ValueError(f"No laps found for driver {driver1}")
        if driver2_laps.empty:
            raise ValueError(f"No laps found for driver {driver2}")

        # Select specific laps or fastest
        if lap1 is not None:
            lap1_data = driver1_laps[driver1_laps['LapNumber'] == lap1].iloc[0]
        else:
            lap1_data = driver1_laps.pick_fastest()

        if lap2 is not None:
            lap2_data = driver2_laps[driver2_laps['LapNumber'] == lap2].iloc[0]
        else:
            lap2_data = driver2_laps.pick_fastest()

        # Get telemetry
        tel1 = lap1_data.get_telemetry().add_distance()
        tel2 = lap2_data.get_telemetry().add_distance()

        if tel1.empty:
            raise ValueError(f"No telemetry data for driver {driver1}")
        if tel2.empty:
            raise ValueError(f"No telemetry data for driver {driver2}")

        # Interpolate onto common distance axis
        max_distance = max(tel1['Distance'].max(), tel2['Distance'].max())
        distance_axis = np.linspace(0, max_distance, settings.TELEMETRY_INTERPOLATION_POINTS)

        # Interpolate both telemetries
        _, tel1_interp = interpolate_telemetry(tel1, settings.TELEMETRY_INTERPOLATION_POINTS)
        _, tel2_interp = interpolate_telemetry(tel2, settings.TELEMETRY_INTERPOLATION_POINTS)

        # Calculate delta time
        delta = calculate_delta_time(tel1, tel2, distance_axis)

        # Get team colors from session results
        # Support both driver abbreviation (e.g., "VER") and driver number (e.g., "1")
        results = session.results
        team1_color = '#CCCCCC'
        team2_color = '#CCCCCC'

        if results is not None and not results.empty:
            # Try to match by abbreviation first, then by driver number
            driver1_results = results[results['Abbreviation'] == driver1]
            if driver1_results.empty:
                # Try matching by driver number (convert to string for comparison)
                driver1_results = results[results['DriverNumber'].astype(str) == str(driver1)]

            if not driver1_results.empty:
                team1_color = safe_get(driver1_results.iloc[0], 'TeamColor', 'CCCCCC')
                team1_color = f"#{team1_color}" if not team1_color.startswith('#') else team1_color

            # Same for driver2
            driver2_results = results[results['Abbreviation'] == driver2]
            if driver2_results.empty:
                # Try matching by driver number (convert to string for comparison)
                driver2_results = results[results['DriverNumber'].astype(str) == str(driver2)]

            if not driver2_results.empty:
                team2_color = safe_get(driver2_results.iloc[0], 'TeamColor', 'CCCCCC')
                team2_color = f"#{team2_color}" if not team2_color.startswith('#') else team2_color

        # Build response
        lap1_info = LapInfo(
            driver=safe_get(lap1_data, 'Driver', driver1),
            driver_number=str(safe_get(lap1_data, 'DriverNumber', 'UNK')),
            team=safe_get(lap1_data, 'Team', 'Unknown'),
            team_color=team1_color,
            lap_number=float(safe_get(lap1_data, 'LapNumber', 0)),
            lap_time=format_timedelta(safe_get(lap1_data, 'LapTime')) or "0:00.000",
            lap_time_seconds=timedelta_to_seconds(safe_get(lap1_data, 'LapTime')) or 0.0
        )

        lap2_info = LapInfo(
            driver=safe_get(lap2_data, 'Driver', driver2),
            driver_number=str(safe_get(lap2_data, 'DriverNumber', 'UNK')),
            team=safe_get(lap2_data, 'Team', 'Unknown'),
            team_color=team2_color,
            lap_number=float(safe_get(lap2_data, 'LapNumber', 0)),
            lap_time=format_timedelta(safe_get(lap2_data, 'LapTime')) or "0:00.000",
            lap_time_seconds=timedelta_to_seconds(safe_get(lap2_data, 'LapTime')) or 0.0
        )

        # Calculate deltas
        lap_time_delta = abs(lap1_info.lap_time_seconds - lap2_info.lap_time_seconds)

        max_speed_delta = 0.0
        if 'speed' in tel1_interp and 'speed' in tel2_interp:
            max_speed_delta = abs(max(tel1_interp['speed']) - max(tel2_interp['speed']))

        # Build comparison data
        comparison_data = {
            "distance": distance_axis.tolist(),
            "driver1_speed": tel1_interp.get('speed', []),
            "driver2_speed": tel2_interp.get('speed', []),
            "driver1_throttle": tel1_interp.get('throttle', []),
            "driver2_throttle": tel2_interp.get('throttle', []),
            "driver1_brake": tel1_interp.get('brake', []),
            "driver2_brake": tel2_interp.get('brake', []),
            "driver1_gear": tel1_interp.get('n_gear', []),
            "driver2_gear": tel2_interp.get('n_gear', []),
            "driver1_rpm": tel1_interp.get('rpm', []),
            "driver2_rpm": tel2_interp.get('rpm', []),
            "driver1_drs": tel1_interp.get('drs', []),
            "driver2_drs": tel2_interp.get('drs', []),
            "delta_time": delta
        }

        return ComparisonTelemetry(
            driver1=lap1_info,
            driver2=lap2_info,
            comparison_data=comparison_data,
            lap_time_delta=lap_time_delta,
            max_speed_delta=max_speed_delta,
            data_points=settings.TELEMETRY_INTERPOLATION_POINTS
        )

    try:
        return await run_in_threadpool(_compare_telemetry)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing telemetry: {str(e)}"
        )


# ============================================================================
# 5. CIRCUIT INFORMATION (1 endpoint)
# ============================================================================

@router.get("/circuit/{year}/{event}", response_model=CircuitInfo, tags=["Circuit"])
async def get_circuit_info(year: int, event: str):
    """
    Get circuit track map and corner information

    Args:
        year: Season year
        event: Event identifier

    Returns:
        Circuit information with track coordinates and corner annotations
    """
    def _get_circuit():
        # Use Race session to get circuit info
        # Need laps=True to get telemetry for track coordinates
        session = get_cached_session(
            year, event, 'R',
            laps=True, telemetry=True, weather=False, messages=False
        )

        # Get circuit info
        circuit_info = session.get_circuit_info()

        # Get track coordinates from fastest lap telemetry
        fastest_lap = session.laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry()

        x_coords = telemetry['X'].tolist() if 'X' in telemetry.columns else []
        y_coords = telemetry['Y'].tolist() if 'Y' in telemetry.columns else []

        # Get corner annotations
        corners = []
        if circuit_info.corners is not None and not circuit_info.corners.empty:
            for _, corner in circuit_info.corners.iterrows():
                corners.append(CornerAnnotation(
                    number=int(safe_get(corner, 'Number', 0)),
                    letter=safe_get(corner, 'Letter'),
                    angle=float(safe_get(corner, 'Angle', 0.0)),
                    distance=safe_get(corner, 'Distance'),
                    x=float(safe_get(corner, 'X', 0.0)),
                    y=float(safe_get(corner, 'Y', 0.0))
                ))

        # Get event info
        event_obj = fastf1.get_event(year, event)
        location = safe_get(event_obj, 'Location', 'Unknown')
        country = safe_get(event_obj, 'Country', 'Unknown')

        return CircuitInfo(
            circuit_name=safe_get(event_obj, 'EventName'),
            location=location,
            country=country,
            rotation=circuit_info.rotation if hasattr(circuit_info, 'rotation') else 0.0,
            track_map=TrackMapData(
                x_coordinates=x_coords,
                y_coordinates=y_coords
            ),
            corners=corners
        )

    try:
        return await run_in_threadpool(_get_circuit)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit info for {event} in {year} not found: {str(e)}"
        )


# ============================================================================
# 6. WEATHER DATA (1 endpoint)
# ============================================================================

@router.get("/weather/{year}/{event}/{session_type}", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(year: int, event: str, session_type: str):
    """
    Get weather data for a session

    Args:
        year: Season year
        event: Event identifier
        session_type: Session type

    Returns:
        Weather data timeline with temperature, wind, rain information
    """
    def _get_weather():
        normalized_session = validate_session_type(session_type)

        # Use cached session with selective loading - only need weather data
        session = get_cached_session(
            year, event, normalized_session,
            laps=False, telemetry=False, weather=True, messages=False
        )

        weather_points = []
        weather_df = session.weather_data

        if weather_df is not None and not weather_df.empty:
            for _, row in weather_df.iterrows():
                weather_points.append(WeatherDataPoint(
                    time=format_timedelta(safe_get(row, 'Time')) or "0:00.000",
                    air_temp=float(safe_get(row, 'AirTemp', 0.0)),
                    humidity=float(safe_get(row, 'Humidity', 0.0)),
                    pressure=float(safe_get(row, 'Pressure', 0.0)),
                    rainfall=bool(safe_get(row, 'Rainfall', False)),
                    track_temp=float(safe_get(row, 'TrackTemp', 0.0)),
                    wind_direction=int(safe_get(row, 'WindDirection', 0)),
                    wind_speed=float(safe_get(row, 'WindSpeed', 0.0))
                ))

        # Calculate summary
        if weather_points:
            avg_air_temp = sum(w.air_temp for w in weather_points) / len(weather_points)
            avg_track_temp = sum(w.track_temp for w in weather_points) / len(weather_points)
            max_wind_speed = max(w.wind_speed for w in weather_points)
            rain_detected = any(w.rainfall for w in weather_points)
        else:
            avg_air_temp = avg_track_temp = max_wind_speed = 0.0
            rain_detected = False

        return WeatherResponse(
            session_info={
                "year": year,
                "event": event,
                "session_type": normalized_session
            },
            weather_data=weather_points,
            summary=WeatherSummary(
                avg_air_temp=avg_air_temp,
                avg_track_temp=avg_track_temp,
                max_wind_speed=max_wind_speed,
                rain_detected=rain_detected
            )
        )

    try:
        return await run_in_threadpool(_get_weather)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Weather data for {event} {session_type} in {year} not found: {str(e)}"
        )


# ============================================================================
# 7. VISUALIZATION HELPERS (2 endpoints)
# ============================================================================

@router.get("/visualization/team-colors/{year}", response_model=TeamColorsResponse, tags=["Visualization"])
async def get_team_colors(year: int):
    """
    Get team colors for a specific season

    Args:
        year: Season year

    Returns:
        List of teams with their official colors
    """
    def _get_colors():
        # Get a race from the season to extract team info
        schedule = fastf1.get_event_schedule(year)
        if schedule.empty:
            raise ValueError(f"No events found for {year}")

        # Get first race
        first_event = schedule.iloc[0]['EventName']
        # Use cached session with selective loading - only need results for team colors
        session = get_cached_session(
            year, first_event, 'R',
            laps=False, telemetry=False, weather=False, messages=False
        )

        teams = []
        results = session.results

        if results is not None and not results.empty:
            seen_teams = set()
            for _, driver in results.iterrows():
                team_name = safe_get(driver, 'TeamName')
                if team_name and team_name not in seen_teams:
                    team_color = safe_get(driver, 'TeamColor', 'CCCCCC')
                    if not team_color.startswith('#'):
                        team_color = f"#{team_color}"

                    teams.append(TeamColor(
                        team_name=team_name,
                        team_id=safe_get(driver, 'TeamId', team_name.lower().replace(' ', '_')),
                        official_color=team_color,
                        fastf1_color=team_color
                    ))
                    seen_teams.add(team_name)

        return TeamColorsResponse(year=year, teams=teams)

    try:
        return await run_in_threadpool(_get_colors)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Team colors for {year} not found: {str(e)}"
        )


@router.get("/visualization/compound-colors", response_model=CompoundColorsResponse, tags=["Visualization"])
async def get_compound_colors_endpoint():
    """
    Get tire compound colors

    Returns:
        List of tire compounds with their colors
    """
    try:
        compound_colors = get_compound_colors()
        compounds = [
            CompoundColor(name=name, color=color)
            for name, color in compound_colors.items()
        ]
        return CompoundColorsResponse(compounds=compounds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching compound colors: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "cache_enabled": settings.FASTF1_CACHE_ENABLED,
        "cache_dir": settings.FASTF1_CACHE_DIR
    }
