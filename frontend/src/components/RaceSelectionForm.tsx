import React, { useState, useEffect, useCallback } from 'react';
import f1ApiService from '../services/f1ApiService';
import { RaceEvent, SessionInfo } from '../types/f1Data';

interface RaceSelectionFormProps {
  onSelectionChange: (year: number | null, gpName: string | null, sessionType: string | null) => void;
}

const RaceSelectionForm: React.FC<RaceSelectionFormProps> = ({ onSelectionChange }) => {
  const [seasons, setSeasons] = useState<number[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [races, setRaces] = useState<RaceEvent[]>([]);
  const [selectedGpName, setSelectedGpName] = useState<string | null>(null);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [selectedSessionType, setSelectedSessionType] = useState<string | null>(null);

  // Fetch Seasons
  useEffect(() => {
    const fetchSeasons = async () => {
      try {
        const data = await f1ApiService.getSeasons();
        setSeasons(data);
        if (data.length > 0) {
          setSelectedYear(data[data.length - 1]); // Select the latest season by default
        }
      } catch (error) {
        console.error("Error fetching seasons:", error);
      }
    };
    fetchSeasons();
  }, []);

  // Fetch Races for selected Year
  useEffect(() => {
    const fetchRaces = async () => {
      if (selectedYear) {
        try {
          const data = await f1ApiService.getRaces(selectedYear);
          setRaces(data);
          if (data.length > 0) {
            setSelectedGpName(data[data.length - 1].event_name); // Select the latest race by default
          }
        } catch (error) {
          console.error(`Error fetching races for year ${selectedYear}:`, error);
        }
      }
    };
    fetchRaces();
  }, [selectedYear]);

  // Fetch Sessions for selected Year and GP Name
  useEffect(() => {
    const fetchSessions = async () => {
      if (selectedYear && selectedGpName) {
        try {
          const data = await f1ApiService.getSessions(selectedYear, selectedGpName);
          setSessions(data);
          if (data.length > 0) {
            // Try to select 'Race' session by default, otherwise the first available
            const raceSession = data.find(s => s.session_type === 'Race');
            setSelectedSessionType(raceSession ? raceSession.session_type : data[0].session_type);
          }
        } catch (error) {
          console.error(`Error fetching sessions for ${selectedGpName} in ${selectedYear}:`, error);
        }
      }
    };
    fetchSessions();
  }, [selectedYear, selectedGpName]);

  // Notify parent on selection change
  useEffect(() => {
    onSelectionChange(selectedYear, selectedGpName, selectedSessionType);
  }, [selectedYear, selectedGpName, selectedSessionType, onSelectionChange]);

  const handleYearChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedYear(Number(event.target.value));
    setSelectedGpName(null); // Reset event when year changes
    setSessions([]); // Reset sessions
    setSelectedSessionType(null); // Reset session type
  };

  const handleGpNameChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedGpName(event.target.value);
    setSessions([]); // Reset sessions
    setSelectedSessionType(null); // Reset session type
  };

  const handleSessionTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSessionType(event.target.value);
  };

  return (
    <div className="race-selection-form">
      <div>
        <label htmlFor="year-select">Year:</label>
        <select id="year-select" value={selectedYear || ''} onChange={handleYearChange}>
          <option value="">Select Year</option>
          {seasons.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="gp-name-select">Grand Prix:</label>
        <select id="gp-name-select" value={selectedGpName || ''} onChange={handleGpNameChange} disabled={!selectedYear}>
          <option value="">Select Grand Prix</option>
          {races.map((race) => (
            <option key={race.event_name} value={race.event_name}>
              {race.event_name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="session-type-select">Session Type:</label>
        <select id="session-type-select" value={selectedSessionType || ''} onChange={handleSessionTypeChange} disabled={!selectedGpName}>
          <option value="">Select Session</option>
          {sessions.map((session) => (
            <option key={session.session_type} value={session.session_type}>
              {session.session_name} ({session.session_type})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default RaceSelectionForm;