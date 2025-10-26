/**
 * F1 API Service
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosError } from 'axios';
import type {
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
  CompoundColorsResponse,
  ErrorResponse,
} from '../types/api';

// API Base URL from environment or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds (telemetry can be slow on first load)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    const message = axiosError.response?.data?.detail || axiosError.message || 'An error occurred';
    throw new Error(message);
  }
  throw error;
};

/**
 * F1 API Service
 */
export const f1Api = {
  // ========================================================================
  // EVENT & SCHEDULE DISCOVERY
  // ========================================================================

  /**
   * Get list of available seasons (2018+)
   */
  getSeasons: async (): Promise<number[]> => {
    try {
      const response = await apiClient.get<SeasonsResponse>('/seasons');
      return response.data.seasons;
    } catch (error) {
      return handleApiError(error);
    }
  },

  /**
   * Get all race events for a specific season
   */
  getEvents: async (year: number): Promise<EventsResponse> => {
    try {
      const response = await apiClient.get<EventsResponse>(`/events/${year}`);
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  /**
   * Get all sessions for a specific event
   */
  getSessions: async (year: number, eventIdentifier: string): Promise<SessionsResponse> => {
    try {
      const response = await apiClient.get<SessionsResponse>(`/events/${year}/${eventIdentifier}/sessions`);
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  /**
   * Get all drivers participating in a session
   */
  getDrivers: async (year: number, event: string, sessionType: string): Promise<DriversResponse> => {
    try {
      const response = await apiClient.get<DriversResponse>(
        `/sessions/${year}/${event}/${sessionType}/drivers`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // SESSION RESULTS
  // ========================================================================

  /**
   * Get complete session results with driver standings
   */
  getSessionResults: async (
    year: number,
    event: string,
    sessionType: string
  ): Promise<SessionResultsResponse> => {
    try {
      const response = await apiClient.get<SessionResultsResponse>(
        `/sessions/${year}/${event}/${sessionType}/results`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // LAP TIMING
  // ========================================================================

  /**
   * Get lap timing data for a session
   */
  getLaps: async (
    year: number,
    event: string,
    sessionType: string,
    options?: {
      driver?: string;
      quicklapsOnly?: boolean;
      excludeDeleted?: boolean;
      limit?: number;
    }
  ): Promise<LapsResponse> => {
    try {
      const params = new URLSearchParams();
      if (options?.driver) params.append('driver', options.driver);
      if (options?.quicklapsOnly) params.append('quicklaps_only', 'true');
      if (options?.excludeDeleted !== false) params.append('exclude_deleted', 'true');
      if (options?.limit) params.append('limit', options.limit.toString());

      const response = await apiClient.get<LapsResponse>(
        `/sessions/${year}/${event}/${sessionType}/laps?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // TELEMETRY COMPARISON (CORE FEATURE)
  // ========================================================================

  /**
   * Compare telemetry between two drivers
   * This is the core feature of the dashboard
   */
  compareTelemetry: async (
    year: number,
    event: string,
    sessionType: string,
    driver1: string,
    driver2: string,
    options?: {
      lap1?: number;
      lap2?: number;
    }
  ): Promise<ComparisonTelemetry> => {
    try {
      const params = new URLSearchParams({
        year: year.toString(),
        event,
        session_type: sessionType,
        driver1,
        driver2,
      });

      if (options?.lap1) params.append('lap1', options.lap1.toString());
      if (options?.lap2) params.append('lap2', options.lap2.toString());

      const response = await apiClient.get<ComparisonTelemetry>(
        `/telemetry/compare?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // CIRCUIT INFORMATION
  // ========================================================================

  /**
   * Get circuit track map and corner information
   */
  getCircuitInfo: async (year: number, event: string): Promise<CircuitInfo> => {
    try {
      const response = await apiClient.get<CircuitInfo>(`/circuit/${year}/${event}`);
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // WEATHER DATA
  // ========================================================================

  /**
   * Get weather data for a session
   */
  getWeather: async (year: number, event: string, sessionType: string): Promise<WeatherResponse> => {
    try {
      const response = await apiClient.get<WeatherResponse>(
        `/weather/${year}/${event}/${sessionType}`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // VISUALIZATION HELPERS
  // ========================================================================

  /**
   * Get team colors for a specific season
   */
  getTeamColors: async (year: number): Promise<TeamColorsResponse> => {
    try {
      const response = await apiClient.get<TeamColorsResponse>(`/visualization/team-colors/${year}`);
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  /**
   * Get tire compound colors
   */
  getCompoundColors: async (): Promise<CompoundColorsResponse> => {
    try {
      const response = await apiClient.get<CompoundColorsResponse>('/visualization/compound-colors');
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  // ========================================================================
  // HEALTH CHECK
  // ========================================================================

  /**
   * Check API health status
   */
  healthCheck: async (): Promise<{ status: string; version: string }> => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },
};

export default f1Api;
