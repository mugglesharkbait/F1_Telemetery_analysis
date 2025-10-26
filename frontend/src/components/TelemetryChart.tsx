/**
 * Telemetry Chart Component
 * Displays speed, throttle, brake, gear comparison charts
 */

import React, { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ScriptableContext,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import type { ComparisonTelemetry } from '../types/api';
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

export const TelemetryChart: React.FC<TelemetryChartProps> = ({ data }) => {
  const { driver1, driver2, comparison_data } = data;

  // Common chart options
  const commonOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#ffffff',
          font: {
            size: 12,
            weight: 'bold',
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#e94560',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Distance (m)',
          color: '#ffffff',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
        ticks: {
          color: '#ffffff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      y: {
        display: true,
        ticks: {
          color: '#ffffff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  };

  // Speed Chart Data
  const speedChartData = {
    labels: comparison_data.distance,
    datasets: [
      {
        label: `${driver1.driver} - ${driver1.team}`,
        data: comparison_data.driver1_speed,
        borderColor: driver1.team_color,
        backgroundColor: driver1.team_color + '40',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4,
      },
      {
        label: `${driver2.driver} - ${driver2.team}`,
        data: comparison_data.driver2_speed,
        borderColor: driver2.team_color,
        backgroundColor: driver2.team_color + '40',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4,
      },
    ],
  };

  const speedOptions: ChartOptions<'line'> = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: 'Speed (km/h)',
          color: '#ffffff',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
        min: 0,
        max: 350,
      },
    },
  };

  // Throttle Chart Data
  const throttleChartData = {
    labels: comparison_data.distance,
    datasets: [
      {
        label: `${driver1.driver} Throttle`,
        data: comparison_data.driver1_throttle,
        borderColor: driver1.team_color,
        backgroundColor: driver1.team_color + '40',
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4,
      },
      {
        label: `${driver2.driver} Throttle`,
        data: comparison_data.driver2_throttle,
        borderColor: driver2.team_color,
        backgroundColor: driver2.team_color + '40',
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const throttleOptions: ChartOptions<'line'> = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: 'Throttle (%)',
          color: '#ffffff',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
        min: 0,
        max: 100,
      },
    },
  };

  // Brake Chart Data
  const brakeChartData = {
    labels: comparison_data.distance,
    datasets: [
      {
        label: `${driver1.driver} Brake`,
        data: comparison_data.driver1_brake.map((b) => (b ? 100 : 0)),
        borderColor: driver1.team_color,
        backgroundColor: driver1.team_color,
        borderWidth: 0,
        pointRadius: 0,
        fill: true,
        stepped: true,
      },
      {
        label: `${driver2.driver} Brake`,
        data: comparison_data.driver2_brake.map((b) => (b ? 100 : 0)),
        borderColor: driver2.team_color,
        backgroundColor: driver2.team_color,
        borderWidth: 0,
        pointRadius: 0,
        fill: true,
        stepped: true,
      },
    ],
  };

  const brakeOptions: ChartOptions<'line'> = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: 'Brake (On/Off)',
          color: '#ffffff',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
        min: 0,
        max: 100,
        ticks: {
          callback: (value) => (value === 0 ? 'Off' : 'On'),
          color: '#ffffff',
        },
      },
    },
  };

  // Gear Chart Data
  const gearChartData = {
    labels: comparison_data.distance,
    datasets: [
      {
        label: `${driver1.driver} Gear`,
        data: comparison_data.driver1_gear,
        borderColor: driver1.team_color,
        backgroundColor: driver1.team_color + '40',
        borderWidth: 2,
        pointRadius: 0,
        stepped: true,
      },
      {
        label: `${driver2.driver} Gear`,
        data: comparison_data.driver2_gear,
        borderColor: driver2.team_color,
        backgroundColor: driver2.team_color + '40',
        borderWidth: 2,
        pointRadius: 0,
        stepped: true,
      },
    ],
  };

  const gearOptions: ChartOptions<'line'> = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: 'Gear',
          color: '#ffffff',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
        min: 0,
        max: 8,
      },
    },
  };

  // Delta Time Chart Data
  const deltaChartData = {
    labels: comparison_data.distance,
    datasets: [
      {
        label: 'Time Delta (s)',
        data: comparison_data.delta_time,
        borderColor: (context: ScriptableContext<'line'>) => {
          const value = context.parsed?.y;
          return value && value > 0 ? driver2.team_color : driver1.team_color;
        },
        backgroundColor: (context: ScriptableContext<'line'>) => {
          const value = context.parsed?.y;
          return value && value > 0 ? driver2.team_color + '40' : driver1.team_color + '40';
        },
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const deltaOptions: ChartOptions<'line'> = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: `Delta Time (s) - Positive = ${driver2.driver} slower`,
          color: '#ffffff',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
      },
    },
  };

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
            <Line data={speedChartData} options={speedOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Time Delta</h3>
          <div className="chart-wrapper">
            <Line data={deltaChartData} options={deltaOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Throttle Application</h3>
          <div className="chart-wrapper">
            <Line data={throttleChartData} options={throttleOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Brake Points</h3>
          <div className="chart-wrapper">
            <Line data={brakeChartData} options={brakeOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Gear Selection</h3>
          <div className="chart-wrapper">
            <Line data={gearChartData} options={gearOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelemetryChart;
