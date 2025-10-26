/**
 * TypeScript interfaces matching the backend Pydantic models
 * These types mirror the backend API responses from schemas.py
 */

// ============================================================================
// COMMON TYPES
// ============================================================================

export interface Point {
  x: number;
  y: number;
  z: number;
}

// ============================================================================
// EVENT & SCHEDULE DISCOVERY
// ============================================================================

export interface SessionInfo {
  session_name: string;
  session_type: string;
  session_number?: number;
  date_utc: string;
  date_local?: string;
}

export interface RaceEventInfo {
  round_number: number;
  event_name: string;
  official_event_name?: string;
  location: string;
  country: string;
  country_code?: string;
  event_date: string;
  event_format?: 'conventional' | 'sprint' | 'sprint_shootout' | 'sprint_qualifying' | 'testing';
  is_testing: boolean;
}

export interface SeasonsResponse {
  seasons: number[];
}

export interface EventsResponse {
  events: RaceEventInfo[];
}

export interface SessionsResponse {
  sessions: SessionInfo[];
}

// ============================================================================
// DRIVER & TEAM INFORMATION
// ============================================================================

export interface DriverInfo {
  driver_number: string;
  abbreviation: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  team_name: string;
  team_color: string;
  country_code?: string;
  headshot_url?: string;
}

export interface DriversResponse {
  drivers: DriverInfo[];
}

export interface DriverResult {
  position?: number;
  driver_number: string;
  broadcast_name: string;
  full_name: string;
  abbreviation: string;
  driver_id: string;
  team_name: string;
  team_color: string;
  team_id: string;
  first_name: string;
  last_name: string;
  headshot_url?: string;
  country_code?: string;
  grid_position?: number;
  classified_position?: string;
  q1?: string;
  q2?: string;
  q3?: string;
  time?: string;
  status?: string;
  points: number;
  laps?: number;
}

export interface SessionResultsResponse {
  session_info: {
    year: number;
    event: string;
    session_type: string;
    session_name: string;
  };
  results: DriverResult[];
}

// ============================================================================
// LAP TIMING & ANALYSIS
// ============================================================================

export interface LapData {
  time: string;
  driver: string;
  driver_number: string;
  lap_time?: string;
  lap_time_seconds?: number;
  lap_number: number;
  lap_start_time?: string;
  lap_start_date?: string;
  stint?: number;
  sector_1_time?: string;
  sector_2_time?: string;
  sector_3_time?: string;
  sector_1_session_time?: string;
  sector_2_session_time?: string;
  sector_3_session_time?: string;
  speed_i1?: number;
  speed_i2?: number;
  speed_fl?: number;
  speed_st?: number;
  is_personal_best: boolean;
  is_accurate: boolean;
  compound?: string;
  tyre_life?: number;
  fresh_tyre?: boolean;
  pit_out_time?: string;
  pit_in_time?: string;
  team?: string;
  track_status?: string;
  position?: number;
  deleted?: boolean;
  deleted_reason?: string;
}

export interface LapsResponse {
  laps: LapData[];
  total_laps: number;
}

// ============================================================================
// TELEMETRY & COMPARISON
// ============================================================================

export interface LapInfo {
  driver: string;
  driver_number: string;
  team: string;
  team_color: string;
  lap_number: number;
  lap_time: string;
  lap_time_seconds: number;
}

export interface ComparisonTelemetry {
  driver1: LapInfo;
  driver2: LapInfo;
  comparison_data: {
    distance: number[];
    driver1_speed: number[];
    driver2_speed: number[];
    driver1_throttle: number[];
    driver2_throttle: number[];
    driver1_brake: boolean[];
    driver2_brake: boolean[];
    driver1_gear: number[];
    driver2_gear: number[];
    driver1_rpm: number[];
    driver2_rpm: number[];
    driver1_drs: number[];
    driver2_drs: number[];
    delta_time: number[];
  };
  lap_time_delta: number;
  max_speed_delta: number;
  data_points: number;
}

// ============================================================================
// CIRCUIT & TRACK INFORMATION
// ============================================================================

export interface CornerAnnotation {
  number: number;
  letter?: string;
  name?: string;
  angle: number;
  distance?: number;
  x: number;
  y: number;
}

export interface TrackMapData {
  x_coordinates: number[];
  y_coordinates: number[];
}

export interface CircuitInfo {
  circuit_name?: string;
  location: string;
  country: string;
  rotation: number;
  track_map: TrackMapData;
  corners: CornerAnnotation[];
  marshal_lights: any[];
  marshal_sectors: any[];
}

// ============================================================================
// WEATHER DATA
// ============================================================================

export interface WeatherDataPoint {
  time: string;
  air_temp: number;
  humidity: number;
  pressure: number;
  rainfall: boolean;
  track_temp: number;
  wind_direction: number;
  wind_speed: number;
}

export interface WeatherSummary {
  avg_air_temp: number;
  avg_track_temp: number;
  max_wind_speed: number;
  rain_detected: boolean;
}

export interface WeatherResponse {
  session_info: {
    year: number;
    event: string;
    session_type: string;
  };
  weather_data: WeatherDataPoint[];
  summary: WeatherSummary;
}

// ============================================================================
// VISUALIZATION HELPERS
// ============================================================================

export interface TeamColor {
  team_name: string;
  team_id: string;
  official_color: string;
  fastf1_color: string;
}

export interface TeamColorsResponse {
  year: number;
  teams: TeamColor[];
}

export interface CompoundColor {
  name: string;
  color: string;
}

export interface CompoundColorsResponse {
  compounds: CompoundColor[];
}

// ============================================================================
// ERROR RESPONSES
// ============================================================================

export interface ErrorResponse {
  detail: string;
  error_type?: string;
  status_code: number;
}

// ============================================================================
// UI STATE TYPES
// ============================================================================

export interface SelectionState {
  year?: number;
  event?: string;
  sessionType?: string;
  driver1?: string;
  driver2?: string;
}

export interface LoadingState {
  seasons: boolean;
  events: boolean;
  sessions: boolean;
  drivers: boolean;
  telemetry: boolean;
  circuit: boolean;
  weather: boolean;
}
