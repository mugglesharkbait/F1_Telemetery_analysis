export interface Point {
  x: number;
  y: number;
  z: number;
}

export interface RaceEvent {
  round_number: number;
  country: string;
  location: string;
  event_name: string;
  event_date: string; // Using string for datetime from backend
}

// 1. Event Discovery Endpoints

export interface SessionInfo {
  session_type: string;
  session_name: string;
  session_date: string; // Using string for datetime from backend
}

export interface DriverInfo {
  driver_id: string;
  full_name: string;
  team_name?: string;
  team_color?: string;
}

// 2. Lap Timing and Analysis Endpoints

export interface LapTimeData {
  driver: string;
  lap_number: number;
  lap_time_s: number;
  tyre_compound: string;
  is_in_lap: boolean;
  is_out_lap: boolean;
}

export interface FastestLap {
  driver: string;
  time: number;
  speed: number;
  team: string;
  lap_number: number;
  gap_to_leader?: number;
}

// 3. Core Telemetry Comparison Endpoint

export interface ComparisonTelemetry {
  distance: number[];
  speed_d1: number[];
  speed_d2: number[];
  gear_d1: number[];
  gear_d2: number[];
  throttle_d1: number[];
  throttle_d2: number[];
  brake_d1: number[]; // Binary: 0 or 1
  brake_d2: number[]; // Binary: 0 or 1
  delta_time: number[];
}

// 4. Circuit and Visualisation Data Endpoints

export interface CornerAnnotation {
  number: number;
  angle: number;
  x: number;
  y: number;
}

export interface CircuitMapData {
  track_coordinates: Point[];
  corner_annotations: CornerAnnotation[];
}

export interface WeatherData {
  time: string; // Using string for datetime from backend
  air_temp: number;
  track_temp: number;
  humidity: number;
  wind_speed: number;
  wind_direction: number;
  rain_indicator: number;
}