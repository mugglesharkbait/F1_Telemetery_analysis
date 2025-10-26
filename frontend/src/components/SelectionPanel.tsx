/**
 * Selection Panel Component
 * Handles year, event, session, and driver selection
 */

import React from 'react';
import type { RaceEventInfo, SessionInfo, DriverInfo } from '../types/api';
import './SelectionPanel.css';

interface SelectionPanelProps {
  // Data
  seasons: number[];
  events: RaceEventInfo[];
  sessions: SessionInfo[];
  drivers: DriverInfo[];

  // Current selections
  selectedYear?: number;
  selectedEvent?: string;
  selectedSession?: string;
  selectedDriver1?: string;
  selectedDriver2?: string;

  // Callbacks
  onYearChange: (year: number) => void;
  onEventChange: (eventName: string) => void;
  onSessionChange: (sessionType: string) => void;
  onDriver1Change: (driverAbbr: string) => void;
  onDriver2Change: (driverAbbr: string) => void;
  onCompare: () => void;

  // Loading states
  loadingSeasons?: boolean;
  loadingEvents?: boolean;
  loadingSessions?: boolean;
  loadingDrivers?: boolean;
}

export const SelectionPanel: React.FC<SelectionPanelProps> = ({
  seasons,
  events,
  sessions,
  drivers,
  selectedYear,
  selectedEvent,
  selectedSession,
  selectedDriver1,
  selectedDriver2,
  onYearChange,
  onEventChange,
  onSessionChange,
  onDriver1Change,
  onDriver2Change,
  onCompare,
  loadingSeasons,
  loadingEvents,
  loadingSessions,
  loadingDrivers,
}) => {
  const canCompare = selectedYear && selectedEvent && selectedSession && selectedDriver1 && selectedDriver2;

  return (
    <div className="selection-panel">
      <h2 className="panel-title">🏎️ F1 Telemetry Comparison</h2>

      <div className="selection-grid">
        {/* Season Selection */}
        <div className="selection-group">
          <label htmlFor="year-select">Season</label>
          <select
            id="year-select"
            value={selectedYear || ''}
            onChange={(e) => onYearChange(Number(e.target.value))}
            disabled={loadingSeasons}
            className="select-input"
          >
            <option value="">Select Season</option>
            {seasons.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Event Selection */}
        <div className="selection-group">
          <label htmlFor="event-select">Race Event</label>
          <select
            id="event-select"
            value={selectedEvent || ''}
            onChange={(e) => onEventChange(e.target.value)}
            disabled={!selectedYear}
            className="select-input"
          >
            <option value="">
              {!selectedYear
                ? "Select a season first"
                : loadingEvents
                ? "Loading events..."
                : events.length === 0
                ? "No events available"
                : "Select Event"}
            </option>
            {!loadingEvents && events.map((event) => (
              <option key={event.round_number} value={event.event_name}>
                {event.round_number}. {event.event_name} ({event.location})
              </option>
            ))}
          </select>
        </div>

        {/* Session Selection */}
        <div className="selection-group">
          <label htmlFor="session-select">Session</label>
          <select
            id="session-select"
            value={selectedSession || ''}
            onChange={(e) => onSessionChange(e.target.value)}
            disabled={!selectedEvent}
            className="select-input"
          >
            <option value="">
              {!selectedEvent
                ? "Select an event first"
                : loadingSessions
                ? "Loading sessions..."
                : sessions.length === 0
                ? "No sessions available"
                : "Select Session"}
            </option>
            {!loadingSessions && sessions.map((session, index) => (
              <option key={`${session.session_type}-${index}`} value={session.session_type}>
                {session.session_name}
              </option>
            ))}
          </select>
        </div>

        {/* Driver 1 Selection */}
        <div className="selection-group">
          <label htmlFor="driver1-select">Driver 1</label>
          <select
            id="driver1-select"
            value={selectedDriver1 || ''}
            onChange={(e) => onDriver1Change(e.target.value)}
            disabled={!selectedSession}
            className="select-input driver-select"
          >
            <option value="">
              {!selectedSession
                ? "Select a session first"
                : loadingDrivers
                ? "Loading drivers..."
                : drivers.length === 0
                ? "No drivers available"
                : "Select Driver 1"}
            </option>
            {!loadingDrivers && drivers
              .filter((d) => d.driver_number !== selectedDriver2)
              .map((driver) => (
                <option
                  key={driver.driver_number}
                  value={driver.driver_number}
                  style={{ color: driver.team_color }}
                >
                  {driver.abbreviation ? `${driver.abbreviation} - ` : ''}{driver.full_name} ({driver.team_name})
                </option>
              ))}
          </select>
          {selectedDriver1 && (
            <div className="driver-badge" style={{ backgroundColor: drivers.find(d => d.driver_number === selectedDriver1)?.team_color }}>
              {drivers.find(d => d.driver_number === selectedDriver1)?.abbreviation || drivers.find(d => d.driver_number === selectedDriver1)?.full_name}
            </div>
          )}
        </div>

        {/* Driver 2 Selection */}
        <div className="selection-group">
          <label htmlFor="driver2-select">Driver 2</label>
          <select
            id="driver2-select"
            value={selectedDriver2 || ''}
            onChange={(e) => onDriver2Change(e.target.value)}
            disabled={!selectedSession}
            className="select-input driver-select"
          >
            <option value="">
              {!selectedSession
                ? "Select a session first"
                : loadingDrivers
                ? "Loading drivers..."
                : drivers.length === 0
                ? "No drivers available"
                : "Select Driver 2"}
            </option>
            {!loadingDrivers && drivers
              .filter((d) => d.driver_number !== selectedDriver1)
              .map((driver) => (
                <option
                  key={driver.driver_number}
                  value={driver.driver_number}
                  style={{ color: driver.team_color }}
                >
                  {driver.abbreviation ? `${driver.abbreviation} - ` : ''}{driver.full_name} ({driver.team_name})
                </option>
              ))}
          </select>
          {selectedDriver2 && (
            <div className="driver-badge" style={{ backgroundColor: drivers.find(d => d.driver_number === selectedDriver2)?.team_color }}>
              {drivers.find(d => d.driver_number === selectedDriver2)?.abbreviation || drivers.find(d => d.driver_number === selectedDriver2)?.full_name}
            </div>
          )}
        </div>

        {/* Compare Button */}
        <div className="selection-group compare-button-group">
          <button
            onClick={onCompare}
            disabled={!canCompare}
            className={`compare-button ${canCompare ? 'active' : 'disabled'}`}
          >
            🏁 Compare Telemetry
          </button>
        </div>
      </div>
    </div>
  );
};

export default SelectionPanel;
