/**
 * Custom React Hooks for F1 Data
 * Centralizes API calls and state management
 */

import { useState, useEffect, useCallback } from 'react';
import f1Api from '../services/apiService';
import type {
  RaceEventInfo,
  SessionInfo,
  DriverInfo,
  ComparisonTelemetry,
  SessionResultsResponse,
  LapsResponse,
  CircuitInfo,
  WeatherResponse,
} from '../types/api';

// ============================================================================
// SEASONS HOOK
// ============================================================================

export function useSeasons() {
  const [seasons, setSeasons] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSeasons = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const seasonsList = await f1Api.getSeasons();
      setSeasons(seasonsList);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load seasons';
      
      if (errorMessage.includes('Network Error') || errorMessage.includes('ERR_CONNECTION_REFUSED')) {
        setError('⏳ Backend is starting up or not reachable. Please wait a moment and try again...');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSeasons();
  }, [loadSeasons]);

  return { seasons, loading, error, refetch: loadSeasons };
}

// ============================================================================
// EVENTS HOOK
// ============================================================================

export function useEvents(year?: number) {
  const [events, setEvents] = useState<RaceEventInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadEvents = useCallback(async (selectedYear: number) => {
    setLoading(true);
    setError(null);
    setEvents([]);
    try {
      const response = await f1Api.getEvents(selectedYear);
      setEvents(response.events);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load events');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year) {
      loadEvents(year);
    }
  }, [year, loadEvents]);

  return { events, loading, error, refetch: loadEvents };
}

// ============================================================================
// SESSIONS HOOK
// ============================================================================

export function useSessions(year?: number, event?: string) {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSessions = useCallback(async (selectedYear: number, selectedEvent: string) => {
    setLoading(true);
    setError(null);
    setSessions([]);
    try {
      const response = await f1Api.getSessions(selectedYear, selectedEvent);
      setSessions(response.sessions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year && event) {
      loadSessions(year, event);
    }
  }, [year, event, loadSessions]);

  return { sessions, loading, error, refetch: loadSessions };
}

// ============================================================================
// DRIVERS HOOK
// ============================================================================

export function useDrivers(year?: number, event?: string, sessionType?: string) {
  const [drivers, setDrivers] = useState<DriverInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDrivers = useCallback(async (
    selectedYear: number,
    selectedEvent: string,
    selectedSessionType: string
  ) => {
    setLoading(true);
    setError(null);
    setDrivers([]);
    try {
      const response = await f1Api.getDrivers(selectedYear, selectedEvent, selectedSessionType);
      setDrivers(response.drivers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load drivers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year && event && sessionType) {
      loadDrivers(year, event, sessionType);
    }
  }, [year, event, sessionType, loadDrivers]);

  return { drivers, loading, error, refetch: loadDrivers };
}

// ============================================================================
// TELEMETRY COMPARISON HOOK
// ============================================================================

interface TelemetryParams {
  year: number;
  event: string;
  sessionType: string;
  driver1: string;
  driver2: string;
  lap1?: number;
  lap2?: number;
}

export function useTelemetryComparison() {
  const [data, setData] = useState<ComparisonTelemetry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const compareTelemetry = useCallback(async (params: TelemetryParams) => {
    const { year, event, sessionType, driver1, driver2, lap1, lap2 } = params;
    
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const telemetryData = await f1Api.compareTelemetry(
        year,
        event,
        sessionType,
        driver1,
        driver2,
        { lap1, lap2 }
      );
      setData(telemetryData);
    } catch (err) {
      let errorMessage = 'Failed to load telemetry data';

      if (err instanceof Error) {
        errorMessage = err.message;

        // Provide helpful messages for common issues
        if (errorMessage.includes('not been loaded') || errorMessage.includes('Session.load')) {
          if (year < 2011) {
            errorMessage = `⚠️ Telemetry data is not available for ${year}. Telemetry data is only available from 2011 onwards. For best results, use years 2018-2025.`;
          } else if (year < 2018) {
            errorMessage = `⚠️ Telemetry data is not available for this session (${event} ${year} ${sessionType}). Some sessions from 2011-2017 may not have complete telemetry. For guaranteed telemetry data, use years 2018-2025.`;
          } else {
            errorMessage = `⚠️ Telemetry data could not be loaded for this session. This session may not have telemetry data available, or the data may be corrupted. Try a different session or use years 2018-2025 for best results.`;
          }
        } else if (errorMessage.includes('No telemetry data')) {
          if (year < 2011) {
            errorMessage = `⚠️ No telemetry data available for ${year}. Telemetry data is only available from 2011 onwards. For best results, use years 2018-2025.`;
          } else if (year < 2018) {
            errorMessage = `⚠️ Limited or no telemetry data for ${year}. Some sessions may not have telemetry. For complete telemetry data, use years 2018-2025.`;
          } else {
            errorMessage = `⚠️ ${errorMessage}. This session may not have telemetry data available.`;
          }
        } else if (errorMessage.includes('No laps found')) {
          errorMessage = `⚠️ ${errorMessage}. This driver may not have participated in this session.`;
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, compareTelemetry, reset };
}

// ============================================================================
// SESSION RESULTS HOOK
// ============================================================================

export function useSessionResults(year?: number, event?: string, sessionType?: string) {
  const [results, setResults] = useState<SessionResultsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadResults = useCallback(async (
    selectedYear: number,
    selectedEvent: string,
    selectedSessionType: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await f1Api.getSessionResults(selectedYear, selectedEvent, selectedSessionType);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load results');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year && event && sessionType) {
      loadResults(year, event, sessionType);
    }
  }, [year, event, sessionType, loadResults]);

  return { results, loading, error, refetch: loadResults };
}

// ============================================================================
// LAPS HOOK
// ============================================================================

interface LapsOptions {
  driver?: string;
  quicklapsOnly?: boolean;
  excludeDeleted?: boolean;
  limit?: number;
}

export function useLaps(
  year?: number,
  event?: string,
  sessionType?: string,
  options?: LapsOptions
) {
  const [laps, setLaps] = useState<LapsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLaps = useCallback(async (
    selectedYear: number,
    selectedEvent: string,
    selectedSessionType: string,
    lapsOptions?: LapsOptions
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await f1Api.getLaps(
        selectedYear,
        selectedEvent,
        selectedSessionType,
        lapsOptions
      );
      setLaps(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load laps');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year && event && sessionType) {
      loadLaps(year, event, sessionType, options);
    }
  }, [year, event, sessionType, options, loadLaps]);

  return { laps, loading, error, refetch: loadLaps };
}

// ============================================================================
// CIRCUIT HOOK
// ============================================================================

export function useCircuit(year?: number, event?: string) {
  const [circuit, setCircuit] = useState<CircuitInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCircuit = useCallback(async (selectedYear: number, selectedEvent: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await f1Api.getCircuitInfo(selectedYear, selectedEvent);
      setCircuit(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load circuit');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year && event) {
      loadCircuit(year, event);
    }
  }, [year, event, loadCircuit]);

  return { circuit, loading, error, refetch: loadCircuit };
}

// ============================================================================
// WEATHER HOOK
// ============================================================================

export function useWeather(year?: number, event?: string, sessionType?: string) {
  const [weather, setWeather] = useState<WeatherResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWeather = useCallback(async (
    selectedYear: number,
    selectedEvent: string,
    selectedSessionType: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await f1Api.getWeather(selectedYear, selectedEvent, selectedSessionType);
      setWeather(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load weather');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (year && event && sessionType) {
      loadWeather(year, event, sessionType);
    }
  }, [year, event, sessionType, loadWeather]);

  return { weather, loading, error, refetch: loadWeather };
}
