/**
 * Main Dashboard Page (Refactored)
 * Clean component using custom hooks for state management
 */

import React, { useState, useEffect } from 'react';
import SelectionPanel from '../components/SelectionPanel';
import TelemetryChart from '../components/TelemetryChart';
import {
  useSeasons,
  useEvents,
  useSessions,
  useDrivers,
  useTelemetryComparison,
} from '../hooks/useF1Data';
// @ts-ignore: allow side-effect import of CSS without type declarations
import './Dashboard.css';

export const DashboardRefactored: React.FC = () => {
  // Selection State
  const [selectedYear, setSelectedYear] = useState<number | undefined>();
  const [selectedEvent, setSelectedEvent] = useState<string | undefined>();
  const [selectedSession, setSelectedSession] = useState<string | undefined>();
  const [selectedDriver1, setSelectedDriver1] = useState<string | undefined>();
  const [selectedDriver2, setSelectedDriver2] = useState<string | undefined>();

  // Data from custom hooks
  const { seasons, loading: loadingSeasons, error: seasonsError, refetch: refetchSeasons } = useSeasons();
  const { events, loading: loadingEvents, error: eventsError } = useEvents(selectedYear);
  const { sessions, loading: loadingSessions, error: sessionsError } = useSessions(selectedYear, selectedEvent);
  const { drivers, loading: loadingDrivers, error: driversError } = useDrivers(
    selectedYear,
    selectedEvent,
    selectedSession
  );
  const { data: telemetryData, loading: loadingTelemetry, error: telemetryError, compareTelemetry } = useTelemetryComparison();

  // Consolidated error from all sources
  const [displayError, setDisplayError] = useState<string | null>(null);

  // Update display error when any hook error changes
  useEffect(() => {
    const errors = [seasonsError, eventsError, sessionsError, driversError, telemetryError];
    const firstError = errors.find(err => err !== null);
    setDisplayError(firstError || null);
  }, [seasonsError, eventsError, sessionsError, driversError, telemetryError]);

  // Handlers
  const handleYearChange = (year: number) => {
    setSelectedYear(year);
    setSelectedEvent(undefined);
    setSelectedSession(undefined);
    setSelectedDriver1(undefined);
    setSelectedDriver2(undefined);
    setDisplayError(null);

    // Show info message for historical years
    if (year < 2011) {
      setDisplayError(
        'ℹ️ Note: Telemetry data is not available for years before 2011. You can browse events and drivers, but telemetry comparison will not work. For full telemetry data, please select years 2018-2025.'
      );
    } else if (year < 2018) {
      setDisplayError(
        '⚠️ Note: Telemetry data for this year may be incomplete. Some sessions might not have telemetry available. For guaranteed complete data, use years 2018-2025.'
      );
    }
  };

  const handleEventChange = (eventName: string) => {
    setSelectedEvent(eventName);
    setSelectedSession(undefined);
    setSelectedDriver1(undefined);
    setSelectedDriver2(undefined);
  };

  const handleSessionChange = (sessionType: string) => {
    setSelectedSession(sessionType);
    setSelectedDriver1(undefined);
    setSelectedDriver2(undefined);
  };

  const handleCompare = async () => {
    if (!selectedYear || !selectedEvent || !selectedSession || !selectedDriver1 || !selectedDriver2) {
      setDisplayError('Please select all options before comparing');
      return;
    }

    await compareTelemetry({
      year: selectedYear,
      event: selectedEvent,
      sessionType: selectedSession,
      driver1: selectedDriver1,
      driver2: selectedDriver2,
    });
  };

  const canCompare = selectedYear && selectedEvent && selectedSession && selectedDriver1 && selectedDriver2;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1 className="main-title">
          <span className="title-emoji">🏎️</span>
          F1 Telemetry Comparison Dashboard
        </h1>
        <p className="subtitle">Analyze driver performance with real-time telemetry data</p>

        <div className="info-banner">
          <strong>📊 Data Availability:</strong> Browse 76 years of F1 history (1950-2025)!
          Telemetry comparison works best for <strong>2018-2025</strong> (full data).
          Years 2011-2017 have partial data. Years before 2011 have no telemetry.
        </div>
      </header>

      <main className="dashboard-content">
        {/* Show initial loading state when backend is starting */}
        {loadingSeasons && seasons.length === 0 && !displayError && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p className="loading-text">Connecting to backend...</p>
            <p className="loading-subtext">Loading F1 data (1950-2025)</p>
          </div>
        )}

        {/* Show error with retry option */}
        {displayError && (
          <div className="error-message">
            <div>
              <span className="error-icon">⚠️</span>
              <span>{displayError}</span>
            </div>
            {displayError.includes('Backend is starting') && (
              <button onClick={refetchSeasons} className="retry-button">
                🔄 Retry Connection
              </button>
            )}
          </div>
        )}

        {/* Main content - only show when we have seasons or are not in initial loading */}
        {(!loadingSeasons || seasons.length > 0 || displayError) && (
          <>
            <SelectionPanel
              seasons={seasons}
              events={events}
              sessions={sessions}
              drivers={drivers}
              selectedYear={selectedYear}
              selectedEvent={selectedEvent}
              selectedSession={selectedSession}
              selectedDriver1={selectedDriver1}
              selectedDriver2={selectedDriver2}
              onYearChange={handleYearChange}
              onEventChange={handleEventChange}
              onSessionChange={handleSessionChange}
              onDriver1Change={setSelectedDriver1}
              onDriver2Change={setSelectedDriver2}
              onCompare={handleCompare}
              loadingSeasons={loadingSeasons}
              loadingEvents={loadingEvents}
              loadingSessions={loadingSessions}
              loadingDrivers={loadingDrivers}
            />
          </>
        )}

        {loadingTelemetry && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p className="loading-text">Loading telemetry data...</p>
            <p className="loading-subtext">This may take 20-30 seconds for first-time data download</p>
          </div>
        )}

        {telemetryData && !loadingTelemetry && (
          <div className="telemetry-container">
            <TelemetryChart data={telemetryData} />
          </div>
        )}

        {!telemetryData && !loadingTelemetry && !displayError && canCompare && (
          <div className="empty-state">
            <div className="empty-state-content">
              <span className="empty-state-icon">🏁</span>
              <h2>Ready to Compare</h2>
              <p>Click "Compare Telemetry" button to view detailed analysis</p>
            </div>
          </div>
        )}

        {!telemetryData && !loadingTelemetry && !canCompare && !loadingSeasons && !displayError && (
          <div className="empty-state">
            <div className="empty-state-content">
              <span className="empty-state-icon">🏁</span>
              <h2>Ready to Compare</h2>
              <p>Select a season, event, session, and two drivers to compare their telemetry</p>
            </div>
          </div>
        )}
      </main>

      <footer className="dashboard-footer">
        <p>Data powered by FastF1 • Built with React + TypeScript + FastAPI</p>
        <p className="footer-subtext">Refactored for maintainability with clean architecture</p>
      </footer>
    </div>
  );
};

export default DashboardRefactored;
