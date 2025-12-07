"""
F1 Data Service
Centralizes all F1 data fetching and processing logic
"""

import fastf1
import pandas as pd
from datetime import datetime
from typing import List, Optional, Tuple
import numpy as np

from app.services.session_manager import SessionManager
from app.core.exceptions import (
    DataNotFoundError,
    DriverNotFoundError,
    TelemetryNotAvailableError,
)
from app.core.utils import (
    format_timedelta,
    timedelta_to_seconds,
    safe_get,
    interpolate_telemetry,
    calculate_delta_time,
)
from app.models.schemas import (
    RaceEventInfo,
    SessionInfo,
    DriverInfo,
    DriverResult,
    LapData,
    LapInfo,
    ComparisonTelemetry,
    CornerAnnotation,
    TrackMapData,
    CircuitInfo,
    WeatherDataPoint,
    WeatherSummary,
    WeatherResponse,
)
from app.core.config import settings


class F1DataService:
    """
    Service class for F1 data operations
    Separates business logic from API endpoints
    """

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self._cached_seasons: Optional[List[int]] = None
        self._drivers_cache: dict = {}

    # ========================================================================
    # SEASONS & EVENTS
    # ========================================================================

    def get_seasons(self) -> List[int]:
        """Get list of all available F1 seasons"""
        if self._cached_seasons is not None:
            return self._cached_seasons

        seasons = []
        current_year = datetime.now().year

        for year in range(1950, current_year + 1):
            try:
                schedule = fastf1.get_event_schedule(year)
                if not schedule.empty:
                    seasons.append(year)
            except Exception:
                pass  # Year not available

        self._cached_seasons = sorted(seasons, reverse=True)
        return self._cached_seasons

    def get_events(self, year: int) -> List[RaceEventInfo]:
        """Get all race events for a specific season"""
        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            raise DataNotFoundError(
                f"Events for year {year} not found", resource="events"
            ) from e

        events = []
        for _, event_data in schedule.iterrows():
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
                is_testing='test' in safe_get(event_data, 'EventName', '').lower()
            ))

        return events

    def get_sessions(self, year: int, event_identifier: str) -> List[SessionInfo]:
        """Get all sessions for a specific event"""
        try:
            event = fastf1.get_event(year, event_identifier)
        except Exception as e:
            raise DataNotFoundError(
                f"Sessions for {event_identifier} in {year} not found",
                resource="sessions"
            ) from e

        sessions = []
        session_types = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R']
        session_names_map = {
            'FP1': 'Practice 1', 'FP2': 'Practice 2', 'FP3': 'Practice 3',
            'Q': 'Qualifying', 'S': 'Sprint', 'SS': 'Sprint Shootout',
            'SQ': 'Sprint Qualifying', 'R': 'Race'
        }

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
                pass  # Session doesn't exist

        return sessions

    # ========================================================================
    # DRIVERS
    # ========================================================================

    def get_drivers(self, year: int, event: str, session_type: str) -> List[DriverInfo]:
        """Get all drivers participating in a session"""
        cache_key = f"{year}_{event}_{session_type}"
        
        if cache_key in self._drivers_cache:
            return self._drivers_cache[cache_key]

        session = self.session_manager.get_session(
            year, event, session_type,
            laps=False, telemetry=False, weather=False
        )

        drivers = []
        results = session.results

        if results is not None and not results.empty:
            for _, driver_data in results.iterrows():
                team_color = safe_get(driver_data, 'TeamColor', 'CCCCCC')
                if not team_color.startswith('#'):
                    team_color = f"#{team_color}"

                drivers.append(DriverInfo(
                    driver_number=str(safe_get(driver_data, 'DriverNumber', 'UNK')),
                    abbreviation=safe_get(driver_data, 'Abbreviation', 'UNK'),
                    full_name=safe_get(driver_data, 'FullName', 'Unknown Driver'),
                    first_name=safe_get(driver_data, 'FirstName', ''),
                    last_name=safe_get(driver_data, 'LastName', ''),
                    team_name=safe_get(driver_data, 'TeamName', 'Unknown Team'),
                    team_color=team_color,
                    country_code=safe_get(driver_data, 'CountryCode', '')
                ))

        self._drivers_cache[cache_key] = drivers
        return drivers

    # ========================================================================
    # SESSION RESULTS
    # ========================================================================

    def get_session_results(
        self, year: int, event: str, session_type: str
    ) -> Tuple[dict, List[DriverResult]]:
        """Get complete session results"""
        session = self.session_manager.get_session(
            year, event, session_type,
            laps=False, telemetry=False, weather=False
        )

        results_data = []
        results_df = session.results

        if results_df is not None and not results_df.empty:
            for _, driver in results_df.iterrows():
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
                    q1=format_timedelta(safe_get(driver, 'Q1')),
                    q2=format_timedelta(safe_get(driver, 'Q2')),
                    q3=format_timedelta(safe_get(driver, 'Q3')),
                    time=format_timedelta(safe_get(driver, 'Time')),
                    status=safe_get(driver, 'Status'),
                    points=float(safe_get(driver, 'Points', 0.0)),
                    laps=safe_get(driver, 'Laps')
                ))

        session_info = {
            "year": year,
            "event": event,
            "session_type": session_type,
            "session_name": session.name if hasattr(session, 'name') else session_type
        }

        return session_info, results_data

    # ========================================================================
    # LAPS
    # ========================================================================

    def get_laps(
        self,
        year: int,
        event: str,
        session_type: str,
        driver: Optional[str] = None,
        quicklaps_only: bool = False,
        exclude_deleted: bool = True,
        limit: Optional[int] = None
    ) -> List[LapData]:
        """Get lap timing data for a session"""
        session = self.session_manager.get_session(
            year, event, session_type,
            laps=True, telemetry=False, weather=False
        )

        laps_df = session.laps

        # Apply filters
        if driver:
            laps_df = laps_df.pick_drivers(driver)
        if quicklaps_only:
            laps_df = laps_df.pick_quicklaps()
        if exclude_deleted:
            laps_df = laps_df.pick_not_deleted()
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

        return laps_data

    # ========================================================================
    # TELEMETRY COMPARISON
    # ========================================================================

    def compare_telemetry(
        self,
        year: int,
        event: str,
        session_type: str,
        driver1: str,
        driver2: str,
        lap1: Optional[int] = None,
        lap2: Optional[int] = None
    ) -> ComparisonTelemetry:
        """Compare telemetry between two drivers"""
        # Check telemetry availability by year
        if year < 2011:
            raise TelemetryNotAvailableError(year, event, session_type)

        # Load session with telemetry
        try:
            session = self.session_manager.get_session(
                year, event, session_type,
                laps=True, telemetry=True, weather=False
            )
        except Exception as e:
            raise TelemetryNotAvailableError(
                year, event, session_type, reason=str(e)
            ) from e

        # Get laps for both drivers
        driver1_laps = session.laps.pick_drivers(driver1)
        driver2_laps = session.laps.pick_drivers(driver2)

        if driver1_laps.empty:
            raise DriverNotFoundError(driver1, f"{event} {year} {session_type}")
        if driver2_laps.empty:
            raise DriverNotFoundError(driver2, f"{event} {year} {session_type}")

        # Select specific laps or fastest
        lap1_data = (
            driver1_laps[driver1_laps['LapNumber'] == lap1].iloc[0]
            if lap1 is not None
            else driver1_laps.pick_fastest()
        )
        lap2_data = (
            driver2_laps[driver2_laps['LapNumber'] == lap2].iloc[0]
            if lap2 is not None
            else driver2_laps.pick_fastest()
        )

        # Get telemetry
        tel1 = lap1_data.get_telemetry().add_distance()
        tel2 = lap2_data.get_telemetry().add_distance()

        if tel1.empty:
            raise TelemetryNotAvailableError(
                year, event, session_type, reason=f"No telemetry for driver {driver1}"
            )
        if tel2.empty:
            raise TelemetryNotAvailableError(
                year, event, session_type, reason=f"No telemetry for driver {driver2}"
            )

        # Interpolate telemetries
        max_distance = max(tel1['Distance'].max(), tel2['Distance'].max())
        distance_axis = np.linspace(0, max_distance, settings.TELEMETRY_INTERPOLATION_POINTS)
        
        _, tel1_interp = interpolate_telemetry(tel1, settings.TELEMETRY_INTERPOLATION_POINTS)
        _, tel2_interp = interpolate_telemetry(tel2, settings.TELEMETRY_INTERPOLATION_POINTS)
        
        delta = calculate_delta_time(tel1, tel2, distance_axis)

        # Get team colors
        team1_color, team2_color = self._get_team_colors(session, driver1, driver2)

        # Build lap info
        lap1_info = self._build_lap_info(lap1_data, driver1, team1_color)
        lap2_info = self._build_lap_info(lap2_data, driver2, team2_color)

        # Calculate deltas
        lap_time_delta = abs(lap1_info.lap_time_seconds - lap2_info.lap_time_seconds)
        max_speed_delta = (
            abs(max(tel1_interp.get('speed', [0])) - max(tel2_interp.get('speed', [0])))
            if 'speed' in tel1_interp and 'speed' in tel2_interp
            else 0.0
        )

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

    def _get_team_colors(self, session, driver1: str, driver2: str) -> Tuple[str, str]:
        """Get team colors for two drivers"""
        results = session.results
        team1_color = '#CCCCCC'
        team2_color = '#CCCCCC'

        if results is not None and not results.empty:
            # Try to match by abbreviation first, then by driver number
            for driver, team_color_var in [(driver1, 'team1_color'), (driver2, 'team2_color')]:
                driver_results = results[results['Abbreviation'] == driver]
                if driver_results.empty:
                    driver_results = results[results['DriverNumber'].astype(str) == str(driver)]
                
                if not driver_results.empty:
                    color = safe_get(driver_results.iloc[0], 'TeamColor', 'CCCCCC')
                    color = f"#{color}" if not color.startswith('#') else color
                    if team_color_var == 'team1_color':
                        team1_color = color
                    else:
                        team2_color = color

        return team1_color, team2_color

    def _build_lap_info(self, lap_data, driver: str, team_color: str) -> LapInfo:
        """Build LapInfo object from lap data"""
        return LapInfo(
            driver=safe_get(lap_data, 'Driver', driver),
            driver_number=str(safe_get(lap_data, 'DriverNumber', 'UNK')),
            team=safe_get(lap_data, 'Team', 'Unknown'),
            team_color=team_color,
            lap_number=float(safe_get(lap_data, 'LapNumber', 0)),
            lap_time=format_timedelta(safe_get(lap_data, 'LapTime')) or "0:00.000",
            lap_time_seconds=timedelta_to_seconds(safe_get(lap_data, 'LapTime')) or 0.0
        )

    # ========================================================================
    # CIRCUIT
    # ========================================================================

    def get_circuit_info(self, year: int, event: str) -> CircuitInfo:
        """Get circuit track map and corner information"""
        session = self.session_manager.get_session(
            year, event, 'R',
            laps=True, telemetry=True, weather=False
        )

        circuit_info = session.get_circuit_info()
        fastest_lap = session.laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry()

        x_coords = telemetry['X'].tolist() if 'X' in telemetry.columns else []
        y_coords = telemetry['Y'].tolist() if 'Y' in telemetry.columns else []

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

        event_obj = fastf1.get_event(year, event)

        return CircuitInfo(
            circuit_name=safe_get(event_obj, 'EventName'),
            location=safe_get(event_obj, 'Location', 'Unknown'),
            country=safe_get(event_obj, 'Country', 'Unknown'),
            rotation=circuit_info.rotation if hasattr(circuit_info, 'rotation') else 0.0,
            track_map=TrackMapData(x_coordinates=x_coords, y_coordinates=y_coords),
            corners=corners
        )

    # ========================================================================
    # WEATHER
    # ========================================================================

    def get_weather(self, year: int, event: str, session_type: str) -> WeatherResponse:
        """Get weather data for a session"""
        session = self.session_manager.get_session(
            year, event, session_type,
            laps=False, telemetry=False, weather=True
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
                "session_type": session_type
            },
            weather_data=weather_points,
            summary=WeatherSummary(
                avg_air_temp=avg_air_temp,
                avg_track_temp=avg_track_temp,
                max_wind_speed=max_wind_speed,
                rain_detected=rain_detected
            )
        )


# Global service instance
_f1_data_service: Optional[F1DataService] = None


def get_f1_data_service() -> F1DataService:
    """Get or create global F1 data service instance"""
    global _f1_data_service
    if _f1_data_service is None:
        from app.services.session_manager import get_session_manager
        _f1_data_service = F1DataService(get_session_manager())
    return _f1_data_service
