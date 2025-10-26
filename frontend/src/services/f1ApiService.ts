import axios from 'axios';
import {
  RaceEvent, DriverInfo, SessionInfo, LapTimeData, FastestLap,
  ComparisonTelemetry, CircuitMapData, WeatherData
} from '../types/f1Data';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const f1ApiService = {
  getSeasons: async (): Promise<number[]> => {
    const response = await axios.get(`${API_BASE_URL}/seasons`);
    return response.data;
  },

  getRaces: async (year: number): Promise<RaceEvent[]> => {
    const response = await axios.get(`${API_BASE_URL}/races/${year}`);
    return response.data;
  },

  getSessions: async (year: number, gpName: string): Promise<SessionInfo[]> => {
    const response = await axios.get(`${API_BASE_URL}/sessions/${year}/${gpName}`);
    return response.data;
  },

  getDrivers: async (year: number, gpName: string, sessionType: string): Promise<DriverInfo[]> => {
    const response = await axios.get(`${API_BASE_URL}/drivers/${year}/${gpName}/${sessionType}`);
    return response.data;
  },

  getSessionLaptimes: async (year: number, gpName: string, sessionType: string): Promise<LapTimeData[]> => {
    const response = await axios.get(`${API_BASE_URL}/session/laptimes/${year}/${gpName}/${sessionType}`);
    return response.data;
  },

  getSessionFastestLaps: async (year: number, gpName: string, sessionType: string): Promise<FastestLap[]> => {
    const response = await axios.get(`${API_BASE_URL}/session/fastest_laps/${year}/${gpName}/${sessionType}`);
    return response.data;
  },

  compareTelemetry: async (
    year: number,
    gpName: string,
    sessionType: string,
    driver1Id: string,
    driver2Id: string
  ): Promise<ComparisonTelemetry> => {
    const response = await axios.get(
      `${API_BASE_URL}/telemetry/compare/${year}/${gpName}/${sessionType}/${driver1Id}/${driver2Id}`
    );
    return response.data;
  },

  getCircuitMapData: async (year: number, gpName: string): Promise<CircuitMapData> => {
    const response = await axios.get(`${API_BASE_URL}/circuit/${year}/${gpName}`);
    return response.data;
  },

  getWeatherData: async (year: number, gpName: string, sessionType: string): Promise<WeatherData[]> => {
    const response = await axios.get(`${API_BASE_URL}/weather/${year}/${gpName}/${sessionType}`);
    return response.data;
  },
};

export default f1ApiService;