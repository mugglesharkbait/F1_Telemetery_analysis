import React, { useState, useEffect, useCallback } from 'react';
import RaceSelectionForm from '../components/RaceSelectionForm';
import f1ApiService from '../services/f1ApiService';
import { DriverInfo, ComparisonTelemetry, CircuitMapData } from '../types/f1Data';

// Placeholder for visualization components
const TelemetryChart: React.FC<{ data: any; title: string }> = ({ title }) => (
  <div className="visualization-section">
    <h3>{title}</h3>
    <p>Telemetry Chart Placeholder</p>
  </div>
);

const TrackMapVisualization: React.FC<{ circuit: CircuitMapData | null }> = () => (
  <div className="visualization-section">
    <h3>Track Map Visualization</h3>
    <p>Track Map Placeholder</p>
  </div>
);

const DriverComparisonPage: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedGpName, setSelectedGpName] = useState<string | null>(null);
  const [selectedSessionType, setSelectedSessionType] = useState<string | null>(null);
  const [drivers, setDrivers] = useState<DriverInfo[]>([]);
  const [driver1Id, setDriver1Id] = useState<string | null>(null);
  const [driver2Id, setDriver2Id] = useState<string | null>(null);
  const [lapSelection, setLapSelection] = useState<string>('Fastest Lap'); // e.g., 'Fastest Lap', 'Lap 35'
  const [comparisonTelemetry, setComparisonTelemetry] = useState<ComparisonTelemetry | null>(null);
  const [circuitMapData, setCircuitMapData] = useState<CircuitMapData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectionChange = useCallback((year: number | null, gpName: string | null, sessionType: string | null) => {
    setSelectedYear(year);
    setSelectedGpName(gpName);
    setSelectedSessionType(sessionType);
    // Reset drivers and comparison data when selection changes
    setDrivers([]);
    setDriver1Id(null);
    setDriver2Id(null);
    setComparisonTelemetry(null);
    setCircuitMapData(null);
    setError(null);
  }, []);

  // Fetch Drivers and Circuit Map Data
  useEffect(() => {
    const fetchData = async () => {
      if (selectedYear && selectedGpName && selectedSessionType) {
        setLoading(true);
        setError(null);
        try {
          // Fetch Drivers
          const fetchedDrivers = await f1ApiService.getDrivers(selectedYear, selectedGpName, selectedSessionType);
          setDrivers(fetchedDrivers);
          if (fetchedDrivers.length >= 2) {
            setDriver1Id(fetchedDrivers[0].driver_id);
            setDriver2Id(fetchedDrivers[1].driver_id);
          } else if (fetchedDrivers.length === 1) {
            setDriver1Id(fetchedDrivers[0].driver_id);
            setDriver2Id(null);
          } else {
            setDriver1Id(null);
            setDriver2Id(null);
          }

          // Fetch Circuit Map Data (sessionType is not needed for this endpoint anymore)
          const fetchedCircuitMapData = await f1ApiService.getCircuitMapData(selectedYear, selectedGpName);
          setCircuitMapData(fetchedCircuitMapData);

        } catch (err: any) {
          console.error("Error fetching drivers or circuit map data:", err);
          setError(err.response?.data?.detail || "Failed to fetch drivers or circuit map data.");
        } finally {
          setLoading(false);
        }
      }
    };
    fetchData();
  }, [selectedYear, selectedGpName, selectedSessionType]);

  const handleAnalyze = async () => {
    if (selectedYear && selectedGpName && selectedSessionType && driver1Id && driver2Id) {
      setLoading(true);
      setError(null);
      try {
        const data = await f1ApiService.compareTelemetry(
          selectedYear,
          selectedGpName,
          selectedSessionType,
          driver1Id,
          driver2Id
        );
        setComparisonTelemetry(data);
      } catch (err: any) {
        console.error("Error fetching comparison telemetry:", err);
        setError(err.response?.data?.detail || "Failed to fetch comparison telemetry.");
      } finally {
        setLoading(false);
      }
    } else {
      setError("Please select all required fields for comparison.");
    }
  };

  const getDriverFullName = (driverId: string | null) => {
    return drivers.find(d => d.driver_id === driverId)?.full_name || driverId;
  };

  const renderSummary = () => {
    if (!comparisonTelemetry || !driver1Id || !driver2Id) return null;

    const driver1FullName = getDriverFullName(driver1Id);
    const driver2FullName = getDriverFullName(driver2Id);

    // Placeholder for actual lap times and delta calculation
    // These would ideally come from a separate endpoint or be calculated here if needed
    const lapTime1 = "N/A"; 
    const lapTime2 = "N/A";
    const finalDelta = comparisonTelemetry.delta_time.length > 0 ? comparisonTelemetry.delta_time[comparisonTelemetry.delta_time.length - 1].toFixed(3) : "N/A";
    const finalDeltaSign = finalDelta !== "N/A" && parseFloat(finalDelta) > 0 ? "+" : "";

    return (
      <div className="summary-area">
        <h2>{`${driver1FullName} vs. ${driver2FullName} - ${selectedYear} ${selectedGpName} - ${selectedSessionType} - ${lapSelection}`}
        </h2>
        <p>Lap Time 1: {driver1FullName}: {lapTime1}</p>
        <p>Lap Time 2: {driver2FullName}: {lapTime2}</p>
        <p>Final Δt: {finalDeltaSign}{finalDelta}s ({driver2FullName} is {finalDeltaSign}{finalDelta}s {parseFloat(finalDelta as string) > 0 ? 'slower' : 'faster'} than {driver1FullName})
        </p>
        {/* <p>Best Sector Comparison: Sector 1: VER (+0.05s)</p> */}
      </div>
    );
  };

  const isAnalyzeButtonDisabled = !selectedYear || !selectedGpName || !selectedSessionType || !driver1Id || !driver2Id || loading;

  return (
    <div className="driver-comparison-page">
      <div className="control-panel">
        <RaceSelectionForm onSelectionChange={handleSelectionChange} />

        <div>
          <label htmlFor="driver1-select">Driver 1 (Reference):</label>
          <select
            id="driver1-select"
            value={driver1Id || ''}
            onChange={(e) => setDriver1Id(e.target.value)}
            disabled={!selectedSessionType || drivers.length === 0}
          >
            <option value="">Select Driver 1</option>
            {drivers.map((driver) => (
              <option key={driver.driver_id} value={driver.driver_id}>
                {driver.full_name} ({driver.driver_id})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="driver2-select">Driver 2 (Comparison):</label>
          <select
            id="driver2-select"
            value={driver2Id || ''}
            onChange={(e) => setDriver2Id(e.target.value)}
            disabled={!selectedSessionType || drivers.length === 0}
          >
            <option value="">Select Driver 2</option>
            {drivers.map((driver) => (
              <option key={driver.driver_id} value={driver.driver_id}>
                {driver.full_name} ({driver.driver_id})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="lap-selection">Lap Selection:</label>
          <select
            id="lap-selection"
            value={lapSelection}
            onChange={(e) => setLapSelection(e.target.value)}
            disabled={!selectedSessionType}
          >
            <option value="Fastest Lap">Fastest Lap</option>
            {/* Add options for specific lap numbers or stint averages later */}
          </select>
        </div>

        <button onClick={handleAnalyze} disabled={isAnalyzeButtonDisabled}>
          {loading ? "Analyzing..." : "ANALYZE"}
        </button>
      </div>

      {error && <div className="error-message">Error: {error}</div>}
      {loading && !error && <div className="loading-message">Fetching and Processing Telemetry...</div>}

      {!loading && !error && !comparisonTelemetry && (
        <div className="loading-message">Select a Session to Begin Analysis.</div>
      )}

      {comparisonTelemetry && (
        <>
          {renderSummary()}
          <div className="main-content">
            <TelemetryChart data={comparisonTelemetry.delta_time} title="Cumulative Delta Time (Δt) Chart" />
            <TrackMapVisualization circuit={circuitMapData} />
            <TelemetryChart data={comparisonTelemetry.speed_d1} title="Speed Trace (Driver 1)" />
            <TelemetryChart data={comparisonTelemetry.speed_d2} title="Speed Trace (Driver 2)" />
            <TelemetryChart data={comparisonTelemetry.gear_d1} title="Gear Trace (Driver 1)" />
            <TelemetryChart data={comparisonTelemetry.gear_d2} title="Gear Trace (Driver 2)" />
            <TelemetryChart data={comparisonTelemetry.throttle_d1} title="Throttle Trace (Driver 1)" />
            <TelemetryChart data={comparisonTelemetry.throttle_d2} title="Throttle Trace (Driver 2)" />
            <TelemetryChart data={comparisonTelemetry.brake_d1} title="Brake Trace (Driver 1)" />
            <TelemetryChart data={comparisonTelemetry.brake_d2} title="Brake Trace (Driver 2)" />
          </div>
        </>
      )}
    </div>
  );
};

export default DriverComparisonPage;
