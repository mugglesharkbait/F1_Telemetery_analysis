/**
 * Chart Configuration Utilities
 * Reusable chart configurations and data transformations for ChartJS
 */

import { ChartOptions, ScriptableContext } from 'chart.js';

// ============================================================================
// COMMON CHART OPTIONS
// ============================================================================

export const getCommonChartOptions = (): ChartOptions<'line'> => ({
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
});

// ============================================================================
// SPECIFIC CHART OPTIONS
// ============================================================================

export const getSpeedChartOptions = (): ChartOptions<'line'> => ({
  ...getCommonChartOptions(),
  scales: {
    ...getCommonChartOptions().scales,
    y: {
      ...getCommonChartOptions().scales?.y,
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
});

export const getThrottleChartOptions = (): ChartOptions<'line'> => ({
  ...getCommonChartOptions(),
  scales: {
    ...getCommonChartOptions().scales,
    y: {
      ...getCommonChartOptions().scales?.y,
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
});

export const getBrakeChartOptions = (): ChartOptions<'line'> => ({
  ...getCommonChartOptions(),
  scales: {
    ...getCommonChartOptions().scales,
    y: {
      ...getCommonChartOptions().scales?.y,
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
});

export const getGearChartOptions = (): ChartOptions<'line'> => ({
  ...getCommonChartOptions(),
  scales: {
    ...getCommonChartOptions().scales,
    y: {
      ...getCommonChartOptions().scales?.y,
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
});

export const getDeltaChartOptions = (driver2Name: string): ChartOptions<'line'> => ({
  ...getCommonChartOptions(),
  scales: {
    ...getCommonChartOptions().scales,
    y: {
      ...getCommonChartOptions().scales?.y,
      title: {
        display: true,
        text: `Delta Time (s) - Positive = ${driver2Name} slower`,
        color: '#ffffff',
        font: {
          size: 14,
          weight: 'bold',
        },
      },
    },
  },
});

// ============================================================================
// CHART DATA BUILDERS
// ============================================================================

interface DriverData {
  driver: string;
  team: string;
  teamColor: string;
}

export const buildSpeedChartData = (
  distance: number[],
  driver1: DriverData,
  speed1: number[],
  driver2: DriverData,
  speed2: number[]
) => ({
  labels: distance,
  datasets: [
    {
      label: `${driver1.driver} - ${driver1.team}`,
      data: speed1,
      borderColor: driver1.teamColor,
      backgroundColor: driver1.teamColor + '40',
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.4,
    },
    {
      label: `${driver2.driver} - ${driver2.team}`,
      data: speed2,
      borderColor: driver2.teamColor,
      backgroundColor: driver2.teamColor + '40',
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.4,
    },
  ],
});

export const buildThrottleChartData = (
  distance: number[],
  driver1: DriverData,
  throttle1: number[],
  driver2: DriverData,
  throttle2: number[]
) => ({
  labels: distance,
  datasets: [
    {
      label: `${driver1.driver} Throttle`,
      data: throttle1,
      borderColor: driver1.teamColor,
      backgroundColor: driver1.teamColor + '40',
      borderWidth: 2,
      pointRadius: 0,
      fill: true,
      tension: 0.4,
    },
    {
      label: `${driver2.driver} Throttle`,
      data: throttle2,
      borderColor: driver2.teamColor,
      backgroundColor: driver2.teamColor + '40',
      borderWidth: 2,
      pointRadius: 0,
      fill: true,
      tension: 0.4,
    },
  ],
});

export const buildBrakeChartData = (
  distance: number[],
  driver1: DriverData,
  brake1: boolean[],
  driver2: DriverData,
  brake2: boolean[]
) => ({
  labels: distance,
  datasets: [
    {
      label: `${driver1.driver} Brake`,
      data: brake1.map((b) => (b ? 100 : 0)),
      borderColor: driver1.teamColor,
      backgroundColor: driver1.teamColor,
      borderWidth: 0,
      pointRadius: 0,
      fill: true,
      stepped: true,
    },
    {
      label: `${driver2.driver} Brake`,
      data: brake2.map((b) => (b ? 100 : 0)),
      borderColor: driver2.teamColor,
      backgroundColor: driver2.teamColor,
      borderWidth: 0,
      pointRadius: 0,
      fill: true,
      stepped: true,
    },
  ],
});

export const buildGearChartData = (
  distance: number[],
  driver1: DriverData,
  gear1: number[],
  driver2: DriverData,
  gear2: number[]
) => ({
  labels: distance,
  datasets: [
    {
      label: `${driver1.driver} Gear`,
      data: gear1,
      borderColor: driver1.teamColor,
      backgroundColor: driver1.teamColor + '40',
      borderWidth: 2,
      pointRadius: 0,
      stepped: true,
    },
    {
      label: `${driver2.driver} Gear`,
      data: gear2,
      borderColor: driver2.teamColor,
      backgroundColor: driver2.teamColor + '40',
      borderWidth: 2,
      pointRadius: 0,
      stepped: true,
    },
  ],
});

export const buildDeltaChartData = (
  distance: number[],
  delta: number[],
  driver1Color: string,
  driver2Color: string
) => ({
  labels: distance,
  datasets: [
    {
      label: 'Time Delta (s)',
      data: delta,
      borderColor: (context: ScriptableContext<'line'>) => {
        const value = context.parsed?.y;
        return value && value > 0 ? driver2Color : driver1Color;
      },
      backgroundColor: (context: ScriptableContext<'line'>) => {
        const value = context.parsed?.y;
        return value && value > 0 ? driver2Color + '40' : driver1Color + '40';
      },
      borderWidth: 2,
      pointRadius: 0,
      fill: true,
      tension: 0.4,
    },
  ],
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export const formatLapTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(3);
  return `${minutes}:${secs.padStart(6, '0')}`;
};

export const formatDelta = (seconds: number): string => {
  const sign = seconds >= 0 ? '+' : '-';
  return `${sign}${Math.abs(seconds).toFixed(3)}s`;
};
