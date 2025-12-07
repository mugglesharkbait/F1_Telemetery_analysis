"""
F1 Telemetry API - V1 Endpoints (Refactored)
Clean, maintainable endpoints using service layer
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional

from app.models.schemas import (
    SeasonsResponse,
    EventsResponse,
    SessionsResponse,
    DriversResponse,
    SessionResultsResponse,
    LapsResponse,
    ComparisonTelemetry,
    CircuitInfo,
    WeatherResponse,
    TeamColorsResponse,
    TeamColor,
    CompoundColorsResponse,
    CompoundColor,
)
from app.core.config import settings
from app.core.exceptions import F1APIException, handle_f1_exception
from app.core.utils import get_compound_colors
from app.services.f1_data_service import get_f1_data_service
import fastf1

router = APIRouter()

# Get service instance
f1_service = get_f1_data_service()


# ============================================================================
# ERROR HANDLER
# ============================================================================

def handle_service_error(func):
    """Decorator to handle service layer exceptions"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except F1APIException as exc:
            raise handle_f1_exception(exc)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(exc)}"
            )
    return wrapper


# ============================================================================
# 1. EVENT & SCHEDULE DISCOVERY
# ============================================================================

@router.get("/seasons", response_model=SeasonsResponse, tags=["Events"])
async def get_seasons():
    """Get list of available F1 seasons"""
    @handle_service_error
    async def _get():
        seasons = await run_in_threadpool(f1_service.get_seasons)
        return SeasonsResponse(seasons=seasons)
    
    return await _get()


@router.get("/events/{year}", response_model=EventsResponse, tags=["Events"])
async def get_events(year: int):
    """Get all race events for a specific season"""
    @handle_service_error
    async def _get():
        events = await run_in_threadpool(f1_service.get_events, year)
        return EventsResponse(events=events)
    
    return await _get()


@router.get("/events/{year}/{event_identifier}/sessions", response_model=SessionsResponse, tags=["Events"])
async def get_sessions(year: int, event_identifier: str):
    """Get all sessions for a specific event"""
    @handle_service_error
    async def _get():
        sessions = await run_in_threadpool(
            f1_service.get_sessions, year, event_identifier
        )
        return SessionsResponse(sessions=sessions)
    
    return await _get()


@router.get("/sessions/{year}/{event}/{session_type}/drivers", response_model=DriversResponse, tags=["Drivers"])
async def get_drivers(year: int, event: str, session_type: str):
    """Get all drivers participating in a session"""
    @handle_service_error
    async def _get():
        drivers = await run_in_threadpool(
            f1_service.get_drivers, year, event, session_type
        )
        return DriversResponse(drivers=drivers)
    
    return await _get()


# ============================================================================
# 2. SESSION RESULTS
# ============================================================================

@router.get("/sessions/{year}/{event}/{session_type}/results", response_model=SessionResultsResponse, tags=["Results"])
async def get_session_results(year: int, event: str, session_type: str):
    """Get complete session results with driver standings"""
    @handle_service_error
    async def _get():
        session_info, results = await run_in_threadpool(
            f1_service.get_session_results, year, event, session_type
        )
        return SessionResultsResponse(
            session_info=session_info,
            results=results
        )
    
    return await _get()


# ============================================================================
# 3. LAP TIMING
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
    """Get lap timing data for a session"""
    @handle_service_error
    async def _get():
        laps = await run_in_threadpool(
            f1_service.get_laps,
            year, event, session_type,
            driver=driver,
            quicklaps_only=quicklaps_only,
            exclude_deleted=exclude_deleted,
            limit=limit
        )
        return LapsResponse(laps=laps, total_laps=len(laps))
    
    return await _get()


# ============================================================================
# 4. TELEMETRY COMPARISON (CORE FEATURE)
# ============================================================================

@router.get("/telemetry/compare", response_model=ComparisonTelemetry, tags=["Telemetry"])
async def compare_telemetry(
    year: int = Query(..., description="Season year"),
    event: str = Query(..., description="Event identifier"),
    session_type: str = Query(..., description="Session type"),
    driver1: str = Query(..., description="First driver"),
    driver2: str = Query(..., description="Second driver"),
    lap1: Optional[int] = Query(None, description="Lap number for driver1"),
    lap2: Optional[int] = Query(None, description="Lap number for driver2")
):
    """
    **CORE ENDPOINT**: Compare telemetry between two drivers
    
    Returns detailed telemetry data interpolated onto a common distance axis.
    """
    @handle_service_error
    async def _get():
        return await run_in_threadpool(
            f1_service.compare_telemetry,
            year, event, session_type,
            driver1, driver2,
            lap1=lap1, lap2=lap2
        )
    
    return await _get()


# ============================================================================
# 5. CIRCUIT INFORMATION
# ============================================================================

@router.get("/circuit/{year}/{event}", response_model=CircuitInfo, tags=["Circuit"])
async def get_circuit_info(year: int, event: str):
    """Get circuit track map and corner information"""
    @handle_service_error
    async def _get():
        return await run_in_threadpool(
            f1_service.get_circuit_info, year, event
        )
    
    return await _get()


# ============================================================================
# 6. WEATHER DATA
# ============================================================================

@router.get("/weather/{year}/{event}/{session_type}", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(year: int, event: str, session_type: str):
    """Get weather data for a session"""
    @handle_service_error
    async def _get():
        return await run_in_threadpool(
            f1_service.get_weather, year, event, session_type
        )
    
    return await _get()


# ============================================================================
# 7. VISUALIZATION HELPERS
# ============================================================================

@router.get("/visualization/team-colors/{year}", response_model=TeamColorsResponse, tags=["Visualization"])
async def get_team_colors(year: int):
    """Get team colors for a specific season"""
    @handle_service_error
    async def _get():
        # Get first event to extract team colors
        schedule = fastf1.get_event_schedule(year)
        if schedule.empty:
            raise HTTPException(404, f"No events found for {year}")
        
        first_event = schedule.iloc[0]['EventName']
        drivers = await run_in_threadpool(
            f1_service.get_drivers, year, first_event, 'R'
        )
        
        # Extract unique teams
        teams = []
        seen_teams = set()
        for driver in drivers:
            if driver.team_name not in seen_teams:
                teams.append(TeamColor(
                    team_name=driver.team_name,
                    team_id=driver.team_name.lower().replace(' ', '_'),
                    official_color=driver.team_color,
                    fastf1_color=driver.team_color
                ))
                seen_teams.add(driver.team_name)
        
        return TeamColorsResponse(year=year, teams=teams)
    
    return await _get()


@router.get("/visualization/compound-colors", response_model=CompoundColorsResponse, tags=["Visualization"])
async def get_compound_colors_endpoint():
    """Get tire compound colors"""
    try:
        compound_colors = get_compound_colors()
        compounds = [
            CompoundColor(name=name, color=color)
            for name, color in compound_colors.items()
        ]
        return CompoundColorsResponse(compounds=compounds)
    except Exception as e:
        raise HTTPException(500, f"Error fetching compound colors: {str(e)}")


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
