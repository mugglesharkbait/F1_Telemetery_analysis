# 🏎️ F1 Telemetry Dashboard

A full-stack web application for comparing Formula 1 driver telemetry data, built with FastAPI and React.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)
![Node](https://img.shields.io/badge/node-22.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.109-green.svg)

## 🎯 Overview

This application allows you to:
- Compare telemetry between any two F1 drivers from 2018-present
- Visualize speed, throttle, brake, and gear data on interactive charts
- Analyze time deltas and performance differences
- Explore historical F1 race data with FastF1 integration

**Built with:**
- **Backend:** FastAPI + FastF1 + Pandas
- **Frontend:** React + TypeScript + Vite + Chart.js
- **Data Source:** Official F1 API (via FastF1)

## ✨ Features

### 📊 Telemetry Comparison
- **Speed Analysis:** Compare driver speeds throughout the lap
- **Time Delta:** See exactly where drivers gain/lose time
- **Throttle Application:** Analyze throttle usage patterns
- **Brake Points:** Compare braking zones
- **Gear Selection:** See gear choices around the track

### 🏁 Data Coverage
- **Seasons:** 1950 to present (76 years of F1 history!)
  - **2018-2025:** Full telemetry data (recommended for comparisons)
  - **2011-2017:** Partial telemetry and timing data
  - **1950-2010:** Historical results and race data
- **Sessions:** Practice, Qualifying, Sprint, Race
- **All Drivers:** Full grid for each session
- **Team Colors:** Dynamic color coding throughout

### ⚡ Performance
- **First Load:** 20-30 seconds (downloading F1 data)
- **Cached Load:** 2-3 seconds (10-20x faster!)
- **Smart Caching:** FastF1 cache for all telemetry data

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+ and npm
- ~10GB disk space (for F1 data cache)

### Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd new_proj
```

**2. Start Backend (Terminal 1)**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs on: `http://localhost:8000`

**3. Start Frontend (Terminal 2)**
```bash
cd frontend
npm install  # First time only
npm run dev
```
Frontend runs on: `http://localhost:5173`

**4. Open in Browser**
```
http://localhost:5173
```


## 📖 Documentation

- **[Backend README](backend/README.md)** - API endpoints and architecture
- **[Frontend README](frontend/README.md)** - React components and styling
- **[Performance Guide](backend/PERFORMANCE_GUIDE.md)** - Understanding FastF1 caching and first-load performance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  - TypeScript + Vite                                     │
│  - Chart.js visualizations                              │
│  - Responsive design                                     │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST
                 │ (localhost:8000/api/v1)
┌────────────────▼────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  - 11 REST API endpoints                                │
│  - Pydantic data validation                             │
│  - Async request handling                               │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│                   FastF1 Library                         │
│  - F1 data fetching                                      │
│  - Telemetry processing                                 │
│  - Local caching                                         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│                Official F1 API                           │
│  - Live timing data                                      │
│  - Historical telemetry                                 │
│  - Session information                                   │
└─────────────────────────────────────────────────────────┘
```

## 🎨 Screenshots

### Dashboard Overview
The main dashboard with season, event, session, and driver selection:
```
┌─────────────────────────────────────────────────┐
│   🏎️ F1 Telemetry Comparison Dashboard          │
├─────────────────────────────────────────────────┤
│                                                 │
│  Season: [2024 ▼]  Event: [Monaco ▼]          │
│  Session: [Q ▼]    Driver 1: [VER ▼]          │
│  Driver 2: [LEC ▼]  [🏁 Compare Telemetry]    │
│                                                 │
├─────────────────────────────────────────────────┤
│  Speed Comparison Chart                         │
│  Time Delta Chart                               │
│  Throttle Application Chart                     │
│  Brake Points Chart                             │
│  Gear Selection Chart                           │
└─────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
new_proj/
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1_endpoints.py   # 11 REST endpoints
│   │   ├── core/
│   │   │   ├── config.py         # Settings
│   │   │   └── utils.py          # Telemetry processing
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic models (30+)
│   │   └── main.py               # FastAPI app
│   ├── fastf1_cache/             # Cached F1 data (~10GB)
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Configuration
│   ├── .env.example
│   ├── Dockerfile
│   ├── pre_warm_cache.py         # Cache warming script
│   ├── README.md
│   └── PERFORMANCE_GUIDE.md
│
├── frontend/                      # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── SelectionPanel.tsx      # UI for selections
│   │   │   ├── SelectionPanel.css
│   │   │   ├── TelemetryChart.tsx      # 5 Chart.js charts
│   │   │   └── TelemetryChart.css
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx           # Main page
│   │   │   └── Dashboard.css
│   │   ├── services/
│   │   │   └── apiService.ts           # API client
│   │   ├── types/
│   │   │   └── api.ts                  # TypeScript types
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json              # npm dependencies
│   ├── .env                      # API URL config
│   ├── .env.example
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── index.html
│   └── README.md
│
├── docker-compose.yml            # Docker orchestration
└── README.md                     # This file
```

## 🔧 API Endpoints

### Phase 1 (MVP) - **IMPLEMENTED & TESTED**

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/seasons` | GET | Get available F1 seasons | ✅ Working |
| `/api/v1/events/{year}` | GET | Get race events for a year | ✅ Working |
| `/api/v1/events/{year}/{event}/sessions` | GET | Get sessions for an event | ✅ Fixed & Working |
| `/api/v1/sessions/{year}/{event}/{session}/drivers` | GET | Get drivers for a session | ✅ Working |
| `/api/v1/telemetry/compare` | GET | **Compare driver telemetry** | ✅ Working |
| `/api/v1/circuit/{year}/{event}` | GET | Get circuit information | ✅ Working |
| `/api/v1/weather/{year}/{event}/{session}` | GET | Get weather data | ✅ Working |
| `/api/v1/sessions/{year}/{event}/{session}/results` | GET | Get session results | ✅ Working |
| `/api/v1/sessions/{year}/{event}/{session}/laps` | GET | Get lap times | ✅ Working |
| `/api/v1/visualization/team-colors/{year}` | GET | Get team colors | ✅ Working |
| `/api/v1/visualization/compound-colors` | GET | Get tire compound colors | ✅ Working |

**Interactive API Docs:** `http://localhost:8000/docs`

### Key Fix: Sessions Endpoint
The sessions endpoint was updated to properly iterate through all F1 session types (FP1, FP2, FP3, Q, S, SS, SQ, R) and return only those that exist for each event. This fixed the issue where sessions dropdown was empty.

## 🎯 Usage Example

### From the UI

1. Open `http://localhost:5173`
2. **Select a season:**
   - **2018-2025:** For full telemetry comparison (recommended)
   - **2011-2017:** For partial data (some sessions may be incomplete)
   - **1950-2010:** For historical browsing (no telemetry)
3. Select: **2024** → **Bahrain** → **Q** → **VER** vs **LEC**
4. Click "Compare Telemetry"
5. Wait 20-30 seconds (first time)
6. View 5 interactive charts!

### From the API

```bash
# Compare Verstappen vs Leclerc at Monaco Qualifying 2024
curl "http://localhost:8000/api/v1/telemetry/compare?year=2024&event=Monaco&session_type=Q&driver1=VER&driver2=LEC"
```

**Response:**
```json
{
  "driver1": {
    "driver": "VER",
    "team": "Red Bull Racing",
    "lap_time": 70.123,
    "lap_number": 12,
    "team_color": "#3671C6"
  },
  "driver2": {
    "driver": "LEC",
    "team": "Ferrari",
    "lap_time": 70.456,
    "lap_number": 11,
    "team_color": "#E8002D"
  },
  "comparison_data": {
    "distance": [0, 10.5, 21.0, ...],
    "driver1_speed": [250, 280, 295, ...],
    "driver2_speed": [248, 278, 293, ...],
    "delta_time": [0, 0.02, 0.05, ...]
  },
  "lap_time_delta": 0.333,
  "max_speed_delta": 5.2,
  "data_points": 1000
}
```

## ⚙️ Configuration

### Backend (`.env`)
```bash
# API Configuration
PROJECT_NAME=F1 Telemetry API
API_V1_PREFIX=/api/v1

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# FastF1 Cache
FASTF1_CACHE_ENABLED=true
FASTF1_CACHE_DIR=fastf1_cache
TELEMETRY_INTERPOLATION_POINTS=1000
```

### Frontend (`.env`)
```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Make sure you're in backend directory
cd backend

# Correct command (with 'app.' prefix)
uvicorn app.main:app --reload

# NOT this:
# uvicorn main:app --reload  ❌
```

### Frontend can't connect to backend
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `frontend/.env` has correct API URL
3. Check CORS settings in `backend/.env`
4. Restart frontend if you installed new packages: `Ctrl+C` then `npm run dev`

### Sessions or drivers dropdown stays disabled
**This has been fixed!** The backend now properly detects all session types (FP1, FP2, FP3, Q, S, SS, SQ, R) for each event.

If dropdowns still don't populate:
1. Check browser DevTools Console (F12) for errors
2. Check Network tab - verify API calls return data
3. Verify backend is running and accessible

### React warnings in console
**Fixed!** Session dropdown now uses unique keys to prevent React warnings.

### "Failed to resolve import react-chartjs-2"
**Fixed!** The dependency is installed. If you see this error:
1. Stop frontend dev server (`Ctrl+C`)
2. Restart: `npm run dev`
3. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### Slow API responses
This is **normal** on first request! FastF1 downloads gigabytes of F1 data.
- **First load:** 20-30 seconds
- **Cached load:** 2-3 seconds

**Speed it up:**
```bash
cd backend
python pre_warm_cache.py
```

See: [PERFORMANCE_GUIDE.md](backend/PERFORMANCE_GUIDE.md)

## 🚢 Deployment

### Docker Compose
```bash
# Build and run both services
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:80
```

### Manual Deployment

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run build
npm run preview
```

## 📊 Tech Stack

### Backend
- **FastAPI** 0.109.0 - Modern async web framework
- **FastF1** 3.6.1 - Official F1 data library
- **Pydantic** 2.5.3 - Data validation
- **Pandas** 2.1.4 - Data manipulation
- **NumPy** 1.26.3 - Numerical computing
- **Uvicorn** 0.27.0 - ASGI server

### Frontend
- **React** 18.3.1 - UI library
- **TypeScript** 5.3.3 - Type safety
- **Vite** 5.1.0 - Build tool
- **Chart.js** 4.4.3 - Data visualization
- **React-ChartJS-2** 5.2.0 - React wrapper
- **Axios** 1.7.2 - HTTP client
- **React Router** 6.22.0 - Navigation
- **D3** 7.9.0 - Advanced visualizations

## 🎓 Learning Resources

- **FastF1 Documentation:** https://docs.fastf1.dev/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **React Documentation:** https://react.dev/
- **Chart.js Documentation:** https://www.chartjs.org/

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional chart types (track maps, tire strategy)
- Multi-driver comparison (3+ drivers)
- Historical season analysis
- Export functionality (PNG, CSV)
- Live timing during race weekends

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **FastF1 Team** - For the incredible F1 data library
- **Formula 1** - For the official API and data
- **FastAPI Team** - For the amazing web framework
- **React Team** - For the UI library

## 📞 Support

For issues or questions:
1. Review [Troubleshooting](#-troubleshooting) section above
2. Check API docs at `http://localhost:8000/docs`
3. Review backend logs in terminal for detailed error messages

## ✅ Status

- ✅ Backend: **Complete** (11 endpoints, full documentation)
- ✅ Frontend: **Complete** (Dashboard, charts, styling)
- ✅ Integration: **Ready** (CORS configured, types match)
- ✅ Documentation: **Complete** (Backend and frontend READMEs)

## 🏁 Ready to Race!

Both backend and frontend are production-ready. Follow the setup instructions above to get started!

**Recommended first comparison:**
- Season: **2024**
- Event: **Bahrain Grand Prix**
- Session: **Q** (Qualifying)
- Drivers: **VER** (Verstappen) vs **LEC** (Leclerc)

The first telemetry load takes 20-30 seconds while FastF1 downloads F1 data. Subsequent loads are 10x faster (2-3 seconds)!

Enjoy comparing F1 telemetry! 🏎️💨
