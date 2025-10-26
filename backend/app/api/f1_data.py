from fastapi import APIRouter, HTTPException
import fastf1
import numpy as np
import pandas as pd
from typing import List, Optional
from datetime import datetime

from app.models.api_v1 import (
    SessionInfo, LapTimeData, FastestLap, ComparisonTelemetry,
    CircuitMapData, CornerAnnotation, WeatherData, DriverInfo, Point
)
from app.models.race import RaceEvent # Keep RaceEvent for /api/v1/races

router = APIRouter()

# Enable cache
fastf1.Cache.enable_cache("fastf1_cache")

_cached_seasons = None

# 1. Event Discovery Endpoints

@router.get("/seasons", response_model=List[int])
async def get_seasons():
    global _cached_seasons
    if _cached_seasons is not None:
        return _cached_seasons

    seasons = []
    current_year = datetime.now().year # Dynamically get current year
    for year in range(1950, current_year + 1):
        try:
            schedule = fastf1.get_event_schedule(year)
            if not schedule.empty:
                seasons.append(year)
        except Exception:
            pass # fastf1 might raise an exception for years with no data
    _cached_seasons = seasons
    return seasons

@router.get("/races/{year}", response_model=List[RaceEvent])
async def get_races(year: int):
    try:
        schedule = fastf1.get_event_schedule(year)
        races = []
        for _, event in schedule.iterrows():
            races.append(RaceEvent(
                round_number=event["RoundNumber"],
                country=event["Country"],
                location=event["Location"],
                event_name=event["EventName"],
                event_date=event["EventDate"]
            ))
        return races
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Races for year {year} not found or data unavailable: {e}")

@router.get("/sessions/{year}/{gp_name}", response_model=List[SessionInfo])
async def get_sessions(year: int, gp_name: str):
    try:
        event = fastf1.get_event(year, gp_name)
        sessions = []
        for _, session_data in event.sessions.iterrows():
            sessions.append(SessionInfo(
                session_type=session_data["SessionType"],
                session_name=session_data["SessionName"],
                session_date=session_data["SessionDate"]
            ))
        return sessions
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Sessions for {gp_name} in {year} not found or data unavailable: {e}")

@router.get("/drivers/{year}/{gp_name}/{session_type}", response_model=List[DriverInfo])
async def get_drivers(year: int, gp_name: str, session_type: str):
    try:
        session = fastf1.get_session(year, gp_name, session_type)
        session.load(laps=True) # Load laps to get driver info reliably
        drivers = []
        for driver_id in session.drivers:
            driver = session.get_driver(driver_id)
            drivers.append(DriverInfo(
                driver_id=driver_id,
                full_name=driver['FullName'],
                team_name=driver['TeamName'],
                team_color=fastf1.plotting.team_color(driver['TeamName'])
            ))
        return drivers
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Drivers for {gp_name} {session_type} in {year} not found or data unavailable: {e}")

# 2. Lap Timing and Analysis Endpoints

@router.get("/session/laptimes/{year}/{gp_name}/{session_type}", response_model=List[LapTimeData])
async def get_session_laptimes(year: int, gp_name: str, session_type: str):
    try:
        session = fastf1.get_session(year, gp_name, session_type)
        session.load(laps=True)
        laptimes = []
        for _, lap in session.laps.iterlaps():
            laptimes.append(LapTimeData(
                driver=lap['Driver'],
                lap_number=lap['LapNumber'],
                lap_time_s=lap['LapTime'].total_seconds() if pd.notna(lap['LapTime']) else 0.0,
                tyre_compound=lap['Compound'],
                is_in_lap=bool(lap['Is and Outlap']),
                is_out_lap=bool(lap['Is an Outlap'])
            ))
        return laptimes
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Lap times for {gp_name} {session_type} in {year} not found or data unavailable: {e}")

@router.get("/session/fastest_laps/{year}/{gp_name}/{session_type}", response_model=List[FastestLap])
async def get_session_fastest_laps(year: int, gp_name: str, session_type: str):
    try:
        session = fastf1.get_session(year, gp_name, session_type)
        session.load(laps=True)
        
        fastest_laps = []
        # Overall fastest lap
        overall_fastest = session.laps.pick_fastest()
        if overall_fastest:
            fastest_laps.append(FastestLap(
                driver=overall_fastest['Driver'],
                time=overall_fastest['LapTime'].total_seconds() if pd.notna(overall_fastest['LapTime']) else 0.0,
                speed=overall_fastest['SpeedI1'] if pd.notna(overall_fastest['SpeedI1']) else 0.0, # Example speed, adjust as needed
                team=overall_fastest['Team'],
                lap_number=overall_fastest['LapNumber'],
                gap_to_leader=0.0
            ))

        # Driver-specific fastest laps
        for driver_id in session.drivers:
            driver_fastest = session.laps.pick_driver(driver_id).pick_fastest()
            if driver_fastest and driver_fastest['Driver'] != overall_fastest['Driver']: # Avoid duplicating overall fastest
                fastest_laps.append(FastestLap(
                    driver=driver_fastest['Driver'],
                    time=driver_fastest['LapTime'].total_seconds() if pd.notna(driver_fastest['LapTime']) else 0.0,
                    speed=driver_fastest['SpeedI1'] if pd.notna(driver_fastest['SpeedI1']) else 0.0,
                    team=driver_fastest['Team'],
                    lap_number=driver_fastest['LapNumber'],
                    gap_to_leader=(driver_fastest['LapTime'] - overall_fastest['LapTime']).total_seconds() if pd.notna(driver_fastest['LapTime']) and pd.notna(overall_fastest['LapTime']) else None
                ))
        return fastest_laps
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Fastest laps for {gp_name} {session_type} in {year} not found or data unavailable: {e}")

# 3. Core Telemetry Comparison Endpoint

@router.get("/telemetry/compare/{year}/{gp_name}/{session_type}/{driver1_id}/{driver2_id}", response_model=ComparisonTelemetry)
async def compare_telemetry(year: int, gp_name: str, session_type: str, driver1_id: str, driver2_id: str):
    try:
        session = fastf1.get_session(year, gp_name, session_type)
        session.load(laps=True, telemetry=True)

        lap1 = session.laps.pick_driver(driver1_id).pick_fastest()
        lap2 = session.laps.pick_driver(driver2_id).pick_fastest()

        if not lap1: raise HTTPException(status_code=404, detail=f"No fastest lap found for driver {driver1_id}")
        if not lap2: raise HTTPException(status_code=404, detail=f"No fastest lap found for driver {driver2_id}")

        tel1 = lap1.get_telemetry().add_distance()
        tel2 = lap2.get_telemetry().add_distance()

        if tel1.empty: raise HTTPException(status_code=404, detail=f"No telemetry data for driver {driver1_id}")
        if tel2.empty: raise HTTPException(status_code=404, detail=f"No telemetry data for driver {driver2_id}")

        # Normalize: Interpolate both laps onto a common distance axis
        # Use a fixed number of points for interpolation
        num_points = 1000
        max_distance = max(tel1['Distance'].max(), tel2['Distance'].max())
        distance_axis = np.linspace(0, max_distance, num_points)

        speed1 = np.interp(distance_axis, tel1['Distance'], tel1['Speed'])
        speed2 = np.interp(distance_axis, tel2['Distance'], tel2['Speed'])
        gear1 = np.interp(distance_axis, tel1['Distance'], tel1['nGear'])
        gear2 = np.interp(distance_axis, tel2['Distance'], tel2['nGear'])
        throttle1 = np.interp(distance_axis, tel1['Distance'], tel1['Throttle'])
        throttle2 = np.interp(distance_axis, tel2['Distance'], tel2['Throttle'])
        
        # Brake data is often binary (0 or 1), so interpolation might not be ideal.
        # For simplicity, we'll interpolate and then round to nearest int (0 or 1)
        brake1_interp = np.interp(distance_axis, tel1['Distance'], tel1['Brake'])
        brake2_interp = np.interp(distance_axis, tel2['Distance'], tel2['Brake'])
        brake1 = np.round(brake1_interp).astype(int)
        brake2 = np.round(brake2_interp).astype(int)

        # Calculate Delta: Use fastf1.utils.delta_time
        # For distance-based delta, we can use the interpolated times.
        time1_interp = np.interp(distance_axis, tel1['Distance'], tel1['Time'].dt.total_seconds())
        time2_interp = np.interp(distance_axis, tel2['Distance'], tel2['Time'].dt.total_seconds())
        delta = time2_interp - time1_interp

        return ComparisonTelemetry(
            distance=distance_axis.tolist(),
            speed_d1=speed1.tolist(),
            speed_d2=speed2.tolist(),
            gear_d1=gear1.tolist(),
            gear_d2=gear2.tolist(),
            throttle_d1=throttle1.tolist(),
            throttle_d2=throttle2.tolist(),
            brake_d1=brake1.tolist(),
            brake_d2=brake2.tolist(),
            delta_time=delta.tolist()
        )
    except HTTPException:
        raise # Re-raise HTTPException
    except Exception as e:
        print(f"Error in compare_telemetry: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing comparison data: {e}")

# 4. Circuit and Visualisation Data Endpoints

@router.get("/circuit/{year}/{gp_name}", response_model=CircuitMapData)
async def get_circuit_map_data(year: int, gp_name: str):
    try:
        # We need a session to get circuit info, pick a common one like 'Race'
        # If 'Race' is not available, fastf1.get_session will raise an error, caught below
        session = fastf1.get_session(year, gp_name, 'R') 
        session.load(laps=True) # Load laps to get telemetry for track coordinates

        # Get track coordinates from a lap's telemetry data
        try:
            if session.laps.empty:
                raise ValueError("Lap data not available for this session to get track coordinates.")
            lap = session.laps.pick_fastest()
            telemetry = lap.get_telemetry()
            
            track_coordinates = []
            if 'X' in telemetry.columns and 'Y' in telemetry.columns:
                for x, y in zip(telemetry['X'], telemetry['Y']):
                    track_coordinates.append(Point(x=x, y=y, z=0)) # Assuming 2D for now
            else:
                raise ValueError("Track coordinates (X, Y) not found in telemetry.")

        except Exception as e:
            print(f"Error getting track coordinates: {e}")
            raise HTTPException(status_code=404, detail=f"Could not retrieve track coordinates for {gp_name}. It might not be available or data is incomplete.") from e
        
        # Get corner annotations
        circuit_info = session.get_circuit_info()
        corner_annotations = []
        if circuit_info.corners is not None:
            for _, corner in circuit_info.corners.iterrows():
                # fastf1.core.Circuit.corners provides X, Y, Number, Angle
                corner_annotations.append(CornerAnnotation(
                    number=corner['Number'],
                    angle=corner['Angle'],
                    x=corner['X'],
                    y=corner['Y']
                ))

        return CircuitMapData(track_coordinates=track_coordinates, corner_annotations=corner_annotations)
    except HTTPException:
        raise # Re-raise HTTPException
    except Exception as e:
        print(f"Error in get_circuit_map_data: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing circuit map data: {e}")

@router.get("/weather/{year}/{gp_name}/{session_type}", response_model=List[WeatherData])
async def get_weather_data(year: int, gp_name: str, session_type: str):
    try:
        session = fastf1.get_session(year, gp_name, session_type)
        session.load(weather=True)
        
        weather_data_list = []
        if session.weather_data is not None and not session.weather_data.empty:
            for _, row in session.weather_data.iterrows():
                weather_data_list.append(WeatherData(
                    time=row['Time'],
                    air_temp=row['AirTemp'],
                    track_temp=row['TrackTemp'],
                    humidity=row['Humidity'],
                    wind_speed=row['WindSpeed'],
                    wind_direction=row['WindDirection'],
                    rain_indicator=int(row['Rainfall']) # Rainfall is boolean, convert to int (0 or 1)
                ))
        return weather_data_list
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Weather data for {gp_name} {session_type} in {year} not found or data unavailable: {e}")