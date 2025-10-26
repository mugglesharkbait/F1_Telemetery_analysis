# 🏎️ F1 Telemetry Dashboard - Frontend

Modern React + TypeScript dashboard for Formula 1 telemetry comparison and analysis.

## Features

### ✅ Implemented

- **Interactive Selection Panel**
  - Season selection (2018-present)
  - Race event selection
  - Session type selection (FP1, FP2, FP3, Q, R)
  - Dual driver selection with team colors

- **Real-time Telemetry Comparison**
  - Speed traces
  - Throttle application
  - Brake points
  - Gear selection
  - Time delta visualization

- **Beautiful UI/UX**
  - Dark mode design
  - F1-themed color scheme (#e94560 red accent)
  - Responsive layout
  - Smooth animations
  - Loading states
  - Error handling

## Tech Stack

- **React** 18.3.1 - UI framework
- **TypeScript** 5.3.3 - Type safety
- **Vite** 5.1.0 - Build tool & dev server
- **React Router** 6.22.0 - Navigation
- **Chart.js** 4.4.3 - Data visualization
- **React-ChartJS-2** 5.2.0 - React wrapper for Chart.js
- **Axios** 1.7.2 - HTTP client
- **D3** 7.9.0 - Advanced visualizations (optional)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Opens at: http://localhost:5173

### Production Build

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SelectionPanel.tsx       # Race/driver selection
│   │   ├── SelectionPanel.css
│   │   ├── TelemetryChart.tsx       # Chart visualizations
│   │   └── TelemetryChart.css
│   ├── pages/
│   │   ├── Dashboard.tsx            # Main dashboard page
│   │   └── Dashboard.css
│   ├── services/
│   │   └── apiService.ts            # Backend API calls
│   ├── types/
│   │   └── api.ts                   # TypeScript interfaces
│   ├── App.tsx                      # Root component
│   ├── App.css                      # Global styles
│   ├── index.tsx                    # Entry point
│   └── index.css                    # Base styles
├── index.html                       # HTML template
├── vite.config.ts                   # Vite configuration
├── tsconfig.json                    # TypeScript config
├── package.json                     # Dependencies
└── .env.example                     # Environment variables template
```

## Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Configure the backend API URL:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Usage Guide

### 1. Start the Backend

Ensure the FastAPI backend is running:

```bash
cd ../backend
uvicorn app.main:app --reload
```

### 2. Start the Frontend

```bash
npm run dev
```

### 3. Use the Dashboard

1. **Select Season**: Choose a year (e.g., 2024)
2. **Select Event**: Pick a race (e.g., Monaco Grand Prix)
3. **Select Session**: Choose session type (Q for Qualifying, R for Race)
4. **Select Drivers**: Pick two drivers to compare
5. **Click "Compare Telemetry"**: View the comparison charts

### First Load Performance

- **First telemetry request**: 20-30 seconds (downloads F1 data)
- **Subsequent requests**: 2-3 seconds (uses cache)

This is normal! The backend caches all data for instant future access.

## Components

### SelectionPanel

Interactive form for selecting:
- Year, Event, Session
- Driver 1 and Driver 2
- Displays team colors dynamically

**Props:**
```typescript
interface SelectionPanelProps {
  seasons: number[];
  events: RaceEventInfo[];
  sessions: SessionInfo[];
  drivers: DriverInfo[];
  selectedYear?: number;
  selectedEvent?: string;
  selectedSession?: string;
  selectedDriver1?: string;
  selectedDriver2?: string;
  onYearChange: (year: number) => void;
  onEventChange: (eventName: string) => void;
  onSessionChange: (sessionType: string) => void;
  onDriver1Change: (driverAbbr: string) => void;
  onDriver2Change: (driverAbbr: string) => void;
  onCompare: () => void;
  loadingSeasons?: boolean;
  loadingEvents?: boolean;
  loadingSessions?: boolean;
  loadingDrivers?: boolean;
}
```

### TelemetryChart

Displays 5 comparison charts:
1. **Speed Comparison** - Speed traces for both drivers
2. **Time Delta** - Time difference at each point
3. **Throttle Application** - Throttle percentage (0-100%)
4. **Brake Points** - Brake application (On/Off)
5. **Gear Selection** - Gear selection (1-8)

**Props:**
```typescript
interface TelemetryChartProps {
  data: ComparisonTelemetry;
}
```

### Dashboard

Main page that orchestrates everything:
- Manages state for all selections
- Loads data from API
- Handles loading/error states
- Renders Selection Panel and Charts

## API Service

All backend communication handled by `apiService.ts`:

```typescript
import f1Api from './services/apiService';

// Get seasons
const seasons = await f1Api.getSeasons();

// Get events
const events = await f1Api.getEvents(2024);

// Get drivers
const drivers = await f1Api.getDrivers(2024, 'Monaco', 'Q');

// Compare telemetry
const telemetry = await f1Api.compareTelemetry(
  2024,
  'Monaco',
  'Q',
  'VER',
  'LEC'
);
```

## Styling

### Color Scheme

- **Primary**: #e94560 (F1 Red)
- **Background**: #0f0f1e (Dark)
- **Secondary Background**: #1a1a2e
- **Text**: #ffffff (White)
- **Muted Text**: #888888

### Team Colors

Team colors are fetched from the backend and applied dynamically to:
- Driver badges
- Chart lines
- Border colors

## TypeScript Types

All types mirror the backend Pydantic models:

```typescript
// See src/types/api.ts for all interfaces
import type {
  ComparisonTelemetry,
  DriverInfo,
  SessionInfo,
  RaceEventInfo
} from './types/api';
```

## Performance Optimization

### Implemented:
- ✅ Lazy loading of data (only load when needed)
- ✅ Proper React hooks (useEffect dependencies)
- ✅ Chart.js point reduction (pointRadius: 0)
- ✅ Responsive design with CSS Grid
- ✅ Memoization of chart options

### Future Optimizations:
- [ ] React.memo for expensive components
- [ ] Virtual scrolling for large datasets
- [ ] Service worker for offline support
- [ ] Code splitting with React.lazy()

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (responsive design)

## Development

### Run in Development Mode

```bash
npm run dev
```

Features:
- Hot Module Replacement (HMR)
- Fast refresh
- TypeScript type checking
- ESLint warnings

### Build for Production

```bash
npm run build
```

Output in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Troubleshooting

### Backend Connection Error

**Problem:** "Failed to load seasons" or network errors

**Solution:**
1. Check backend is running: http://localhost:8000/health
2. Verify CORS is enabled in backend
3. Check `.env` has correct API URL

### Slow Telemetry Loading

**Problem:** Takes 20-30 seconds to load telemetry

**Solution:** This is normal for first request! Backend downloads F1 data. Subsequent requests are fast (<3s).

### Charts Not Rendering

**Problem:** Charts are empty or not displaying

**Solution:**
1. Check browser console for errors
2. Verify Chart.js is installed: `npm install chart.js react-chartjs-2`
3. Clear browser cache

### TypeScript Errors

**Problem:** Type errors in IDE

**Solution:**
1. Run `npm install` to ensure all type definitions are installed
2. Restart TypeScript server in your IDE
3. Check `tsconfig.json` is correct

## Testing

### Manual Testing Checklist

- [ ] Select season loads events
- [ ] Select event loads sessions
- [ ] Select session loads drivers
- [ ] Select two drivers enables compare button
- [ ] Compare button loads telemetry
- [ ] Charts render with correct data
- [ ] Team colors display correctly
- [ ] Responsive on mobile
- [ ] Error messages display properly
- [ ] Loading states show during data fetch

## Future Enhancements

### Phase 2
- [ ] Lap time comparison table
- [ ] Fastest lap highlights
- [ ] Tire strategy visualization
- [ ] Weather overlay

### Phase 3
- [ ] Circuit track map with speed overlay
- [ ] Position changes graph
- [ ] Driver consistency metrics
- [ ] Export data to CSV/PDF

### Phase 4
- [ ] Real-time live timing (during race weekends)
- [ ] Historical season comparisons
- [ ] Driver championship calculator
- [ ] Social sharing features

## Contributing

See main project README for contribution guidelines.

## License

MIT License

## Support

For issues and questions:
- Check the API documentation: http://localhost:8000/docs
- Review backend logs for API errors
- Check browser console for frontend errors

---

**Built with ❤️ for F1 fans by F1 fans** 🏁
