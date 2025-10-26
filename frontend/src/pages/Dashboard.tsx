/**
 * Main Dashboard Page
 * Orchestrates the entire F1 telemetry comparison experience
 */

import React, { useState, useEffect } from 'react';
import f1Api from '../services/apiService';
import SelectionPanel from '../components/SelectionPanel';
import TelemetryChart from '../components/TelemetryChart';
import type {
  RaceEventInfo,
  SessionInfo,
  DriverInfo,
  ComparisonTelemetry,
} from '../types/api';
// @ts-ignore: allow side-effect import of CSS without type declarations
import './Dashboard.css';

export const Dashboard: React.FC = () => {
  // Data State
  const [seasons, setSeasons] = useState<number[]>([]);
  const [events, setEvents] = useState<RaceEventInfo[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [drivers, setDrivers] = useState<DriverInfo[]>([]);
  const [telemetryData, setTelemetryData] = useState<ComparisonTelemetry | null>(null);

  // Selection State
  const [selectedYear, setSelectedYear] = useState<number | undefined>();
  const [selectedEvent, setSelectedEvent] = useState<string | undefined>();
  const [selectedSession, setSelectedSession] = useState<string | undefined>();
  const [selectedDriver1, setSelectedDriver1] = useState<string | undefined>();
  const [selectedDriver2, setSelectedDriver2] = useState<string | undefined>();

  // Loading State
  const [loadingSeasons, setLoadingSeasons] = useState(false);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [loadingDrivers, setLoadingDrivers] = useState(false);
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);

  // Error State
  const [error, setError] = useState<string | null>(null);

  // Load seasons on mount
  useEffect(() => {
    loadSeasons();
  }, []);

  // Load events when year changes
  useEffect(() => {
    if (selectedYear) {
      loadEvents(selectedYear);
    }
  }, [selectedYear]);

  // Load sessions when event changes
  useEffect(() => {
    if (selectedYear && selectedEvent) {
      loadSessions(selectedYear, selectedEvent);
    }
  }, [selectedYear, selectedEvent]);

  // Load drivers when session changes
  useEffect(() => {
    if (selectedYear && selectedEvent && selectedSession) {
      loadDrivers(selectedYear, selectedEvent, selectedSession);
    }
  }, [selectedYear, selectedEvent, selectedSession]);

  const loadSeasons = async () => {
    setLoadingSeasons(true);
    setError(null);
    try {
      const seasonsList = await f1Api.getSeasons();
      setSeasons(seasonsList);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load seasons';

      // Check if it's a network error (backend not responding)
      if (errorMessage.includes('Network Error') || errorMessage.includes('ERR_CONNECTION_REFUSED') || errorMessage.includes('fetch')) {
        setError('⏳ Backend is starting up or not reachable. Please wait a moment and try again...');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoadingSeasons(false);
    }
  };

  const loadEvents = async (year: number) => {
    setLoadingEvents(true);
    setError(null);
    setEvents([]);
    setSessions([]);
    setDrivers([]);
    setTelemetryData(null);
    try {
      const response = await f1Api.getEvents(year);
      setEvents(response.events);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load events');
    } finally {
      setLoadingEvents(false);
    }
  };

  const loadSessions = async (year: number, event: string) => {
    setLoadingSessions(true);
    setError(null);
    setSessions([]);
    setDrivers([]);
    setTelemetryData(null);
    try {
      const response = await f1Api.getSessions(year, event);
      setSessions(response.sessions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadDrivers = async (year: number, event: string, sessionType: string) => {
    setLoadingDrivers(true);
    setError(null);
    setDrivers([]);
    setTelemetryData(null);
    try {
      const response = await f1Api.getDrivers(year, event, sessionType);
      setDrivers(response.drivers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load drivers');
    } finally {
      setLoadingDrivers(false);
    }
  };

  const handleCompare = async () => {
    if (!selectedYear || !selectedEvent || !selectedSession || !selectedDriver1 || !selectedDriver2) {
      setError('Please select all options before comparing');
      return;
    }

    setLoadingTelemetry(true);
    setError(null);
    setTelemetryData(null);

    try {
      const data = await f1Api.compareTelemetry(
        selectedYear,
        selectedEvent,
        selectedSession,
        selectedDriver1,
        selectedDriver2
      );
      setTelemetryData(data);
    } catch (err) {
      let errorMessage = 'Failed to load telemetry data';

      if (err instanceof Error) {
        errorMessage = err.message;

        // Provide helpful messages for common issues
        if (errorMessage.includes('not been loaded') || errorMessage.includes('Session.load')) {
          // FastF1 telemetry loading error
          if (selectedYear && selectedYear < 2011) {
            errorMessage = `⚠️ Telemetry data is not available for ${selectedYear}. Telemetry data is only available from 2011 onwards. For best results, use years 2018-2025.`;
          } else if (selectedYear && selectedYear < 2018) {
            errorMessage = `⚠️ Telemetry data is not available for this session (${selectedEvent} ${selectedYear} ${selectedSession}). Some sessions from 2011-2017 may not have complete telemetry. For guaranteed telemetry data, use years 2018-2025.`;
          } else {
            errorMessage = `⚠️ Telemetry data could not be loaded for this session. This session may not have telemetry data available, or the data may be corrupted. Try a different session or use years 2018-2025 for best results.`;
          }
        } else if (errorMessage.includes('No telemetry data')) {
          if (selectedYear && selectedYear < 2011) {
            errorMessage = `⚠️ No telemetry data available for ${selectedYear}. Telemetry data is only available from 2011 onwards. For best results, use years 2018-2025.`;
          } else if (selectedYear && selectedYear < 2018) {
            errorMessage = `⚠️ Limited or no telemetry data for ${selectedYear}. Some sessions may not have telemetry. For complete telemetry data, use years 2018-2025.`;
          } else {
            errorMessage = `⚠️ ${errorMessage}. This session may not have telemetry data available.`;
          }
        } else if (errorMessage.includes('No laps found')) {
          errorMessage = `⚠️ ${errorMessage}. This driver may not have participated in this session.`;
        }
      }

      setError(errorMessage);
    } finally {
      setLoadingTelemetry(false);
    }
  };

  const handleYearChange = (year: number) => {
    setSelectedYear(year);
    setSelectedEvent(undefined);
    setSelectedSession(undefined);
    setSelectedDriver1(undefined);
    setSelectedDriver2(undefined);

    // Clear any existing errors
    setError(null);

    // Show info message for historical years
    if (year < 2011) {
      setError('ℹ️ Note: Telemetry data is not available for years before 2011. You can browse events and drivers, but telemetry comparison will not work. For full telemetry data, please select years 2018-2025.');
    } else if (year < 2018) {
      setError('⚠️ Note: Telemetry data for this year may be incomplete. Some sessions might not have telemetry available. For guaranteed complete data, use years 2018-2025.');
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
        {loadingSeasons && seasons.length === 0 && !error && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p className="loading-text">Connecting to backend...</p>
            <p className="loading-subtext">Loading F1 data (1950-2025)</p>
          </div>
        )}

        {/* Show error with retry option */}
        {error && (
          <div className="error-message">
            <div>
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
            {error.includes('Backend is starting') && (
              <button onClick={loadSeasons} className="retry-button">
                🔄 Retry Connection
              </button>
            )}
          </div>
        )}

        {/* Main content - only show when we have seasons or are not in initial loading */}
        {(!loadingSeasons || seasons.length > 0 || error) && (
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

        {!telemetryData && !loadingTelemetry && !error && (
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
      </footer>
    </div>
  );
};

export default Dashboard;
