/**
 * Telemetry Chart Component (Refactored)
 * Clean component using chart utilities for configuration
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import type { ComparisonTelemetry } from '../types/api';
import {
  getSpeedChartOptions,
  getThrottleChartOptions,
  getBrakeChartOptions,
  getGearChartOptions,
  getDeltaChartOptions,
  buildSpeedChartData,
  buildThrottleChartData,
  buildBrakeChartData,
  buildGearChartData,
  buildDeltaChartData,
} from '../utils/chartUtils';
import './TelemetryChart.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TelemetryChartProps {
  data: ComparisonTelemetry;
}

export const TelemetryChartRefactored: React.FC<TelemetryChartProps> = ({ data }) => {
  const { driver1, driver2, comparison_data } = data;

  // Build driver data objects for utility functions
  const driver1Data = {
    driver: driver1.driver,
    team: driver1.team,
    teamColor: driver1.team_color,
  };

  const driver2Data = {
    driver: driver2.driver,
    team: driver2.team,
    teamColor: driver2.team_color,
  };

  // Build chart data using utilities
  const speedData = buildSpeedChartData(
    comparison_data.distance,
    driver1Data,
    comparison_data.driver1_speed,
    driver2Data,
    comparison_data.driver2_speed
  );

  const throttleData = buildThrottleChartData(
    comparison_data.distance,
    driver1Data,
    comparison_data.driver1_throttle,
    driver2Data,
    comparison_data.driver2_throttle
  );

  const brakeData = buildBrakeChartData(
    comparison_data.distance,
    driver1Data,
    comparison_data.driver1_brake,
    driver2Data,
    comparison_data.driver2_brake
  );

  const gearData = buildGearChartData(
    comparison_data.distance,
    driver1Data,
    comparison_data.driver1_gear,
    driver2Data,
    comparison_data.driver2_gear
  );

  const deltaData = buildDeltaChartData(
    comparison_data.distance,
    comparison_data.delta_time,
    driver1.team_color,
    driver2.team_color
  );

  // Get chart options
  const speedOptions = getSpeedChartOptions();
  const throttleOptions = getThrottleChartOptions();
  const brakeOptions = getBrakeChartOptions();
  const gearOptions = getGearChartOptions();
  const deltaOptions = getDeltaChartOptions(driver2.driver);

  return (
    <div className="telemetry-charts">
      {/* Summary Stats */}
      <div className="telemetry-summary">
        <div className="summary-card" style={{ borderColor: driver1.team_color }}>
          <h3 style={{ color: driver1.team_color }}>{driver1.driver}</h3>
          <p className="team-name">{driver1.team}</p>
          <p className="lap-time">{driver1.lap_time}</p>
          <p className="lap-number">Lap {driver1.lap_number}</p>
        </div>

        <div className="vs-divider">VS</div>

        <div className="summary-card" style={{ borderColor: driver2.team_color }}>
          <h3 style={{ color: driver2.team_color }}>{driver2.driver}</h3>
          <p className="team-name">{driver2.team}</p>
          <p className="lap-time">{driver2.lap_time}</p>
          <p className="lap-number">Lap {driver2.lap_number}</p>
        </div>

        <div className="delta-card">
          <h4>Lap Time Delta</h4>
          <p className="delta-time">{data.lap_time_delta.toFixed(3)}s</p>
          <p className="max-speed-delta">
            Max Speed Δ: {data.max_speed_delta.toFixed(1)} km/h
          </p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        <div className="chart-container">
          <h3 className="chart-title">Speed Comparison</h3>
          <div className="chart-wrapper">
            <Line data={speedData} options={speedOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Time Delta</h3>
          <div className="chart-wrapper">
            <Line data={deltaData} options={deltaOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Throttle Application</h3>
          <div className="chart-wrapper">
            <Line data={throttleData} options={throttleOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Brake Points</h3>
          <div className="chart-wrapper">
            <Line data={brakeData} options={brakeOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Gear Selection</h3>
          <div className="chart-wrapper">
            <Line data={gearData} options={gearOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelemetryChartRefactored;
