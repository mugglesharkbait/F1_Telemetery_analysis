# F1 Telemetry API - Backend

High-performance FastAPI backend for Formula 1 telemetry and timing data analysis.

## Features

### Phase 1 (MVP) - Implemented ✅

1. **Event & Schedule Discovery**
   - `GET /api/v1/seasons` - List available seasons (2018+)
   - `GET /api/v1/events/{year}` - Get all race events for a season
   - `GET /api/v1/events/{year}/{event}/sessions` - Get sessions for an event
   - `GET /api/v1/sessions/{year}/{event}/{session_type}/drivers` - Get drivers in a session

2. **Session Results**
   - `GET /api/v1/sessions/{year}/{event}/{session_type}/results` - Complete session results

3. **Lap Timing**
   - `GET /api/v1/sessions/{year}/{event}/{session_type}/laps` - All lap times with filtering

4. **Telemetry Comparison (Core Feature)**
   - `GET /api/v1/telemetry/compare` - Compare telemetry between two drivers

5. **Circuit Information**
   - `GET /api/v1/circuit/{year}/{event}` - Track map and corner annotations

6. **Weather Data**
   - `GET /api/v1/weather/{year}/{event}/{session_type}` - Session weather timeline

7. **Visualization Helpers**
   - `GET /api/v1/visualization/team-colors/{year}` - Team colors for season
   - `GET /api/v1/visualization/compound-colors` - Tire compound colors

## Tech Stack

- **FastAPI** 0.109.0 - Modern async web framework
- **FastF1** 3.6.1 - Official F1 data library
- **Pandas** 2.1.4 - Data manipulation
- **NumPy** 1.26.3 - Numerical computing
- **Pydantic** 2.5.3 - Data validation
- **Uvicorn** 0.27.0 - ASGI server

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker

1. **Build the image:**
   ```bash
   docker build -t f1-telemetry-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 \
     -v $(pwd)/fastf1_cache:/app/fastf1_cache \
     f1-telemetry-api
   ```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1_endpoints.py       # All Phase 1 API endpoints
│   │   └── f1_data.py            # Legacy endpoints (deprecated)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Application settings
│   │   └── utils.py              # Utility functions (formatting, interpolation)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py            # Comprehensive Pydantic models
│   │   ├── race.py               # Legacy models
│   │   ├── driver.py             # Legacy models
│   │   ├── circuit.py            # Legacy models
│   │   └── comparison.py         # Legacy models
│   └── main.py                   # FastAPI application entry point
├── fastf1_cache/                 # FastF1 data cache (auto-generated)
├── Dockerfile                    # Production container
├── requirements.txt              # Python dependencies
├── start.sh                      # Startup script
└── .env.example                  # Environment variables template
```

## API Endpoints

### Example Requests

#### Get Available Seasons
```bash
curl http://localhost:8000/api/v1/seasons
```

Response:
```json
{
  "seasons": [2024, 2023, 2022, 2021, 2020, 2019, 2018]
}
```

#### Get Race Events for 2024
```bash
curl http://localhost:8000/api/v1/events/2024
```

#### Get Drivers for Monaco 2024 Race
```bash
curl http://localhost:8000/api/v1/sessions/2024/Monaco/R/drivers
```

#### Compare Telemetry (Core Feature)
```bash
curl "http://localhost:8000/api/v1/telemetry/compare?year=2024&event=Monaco&session_type=Q&driver1=VER&driver2=LEC"
```

This returns detailed telemetry comparison with:
- Speed, throttle, brake, gear data for both drivers
- Time delta at each distance point
- 1000 interpolated data points for smooth visualization

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key settings:
- `FASTF1_CACHE_DIR` - Directory for FastF1 data cache
- `TELEMETRY_INTERPOLATION_POINTS` - Number of points for telemetry interpolation (default: 1000)
- `CORS_ORIGINS` - Allowed frontend origins

## Data Processing

### Telemetry Interpolation

The API interpolates telemetry data onto a common distance axis to enable accurate comparisons:

1. **Load telemetry** for both drivers
2. **Add distance** channel using `add_distance()`
3. **Create common axis** with N points (default: 1000)
4. **Interpolate** all channels (speed, throttle, brake, gear, etc.)
5. **Calculate delta time** between the two laps

### Async Operations

All FastF1 operations are wrapped in `run_in_threadpool` to prevent blocking the event loop:

```python
data = await run_in_threadpool(load_fastf1_data, year, event, session)
```

## Caching

FastF1 automatically caches all downloaded data to avoid repeated API calls:

- Cache location: `fastf1_cache/` (configurable)
- Persistent across container restarts when using volumes
- Significantly improves response times for subsequent requests

## Performance

- **First request** (cold cache): 5-30 seconds (depends on data size)
- **Cached requests**: < 1 second
- **Telemetry comparison**: 2-5 seconds (includes interpolation)

## Error Handling

The API provides detailed error messages:

- `404` - Data not found (invalid year/event/session)
- `400` - Invalid parameters
- `500` - Server error (with error details)

## Health Checks

- `GET /health` - Global health check
- `GET /api/v1/health` - API-specific health with cache status

## Development

### Adding New Endpoints

1. Add Pydantic models to `app/models/schemas.py`
2. Add endpoint to `app/api/v1_endpoints.py`
3. Use `run_in_threadpool` for FastF1 operations
4. Add proper error handling
5. Update this README

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Keep functions focused and small

## Testing

```bash
# Run the server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test seasons endpoint
curl http://localhost:8000/api/v1/seasons

# Test telemetry comparison
curl "http://localhost:8000/api/v1/telemetry/compare?year=2024&event=Monaco&session_type=Q&driver1=VER&driver2=LEC"
```

## Troubleshooting

### FastF1 Data Not Loading

- Ensure internet connection for first-time data fetch
- Check FastF1 cache directory permissions
- FastF1 data is available from 2018 onwards

### Slow Response Times

- First request downloads data (can take 30s)
- Subsequent requests use cache (< 1s)
- Mount cache directory as volume in Docker

### CORS Errors

- Add frontend URL to `CORS_ORIGINS` in `.env`
- Restart server after changing settings

## Future Phases

### Phase 2 (Coming Soon)
- Fastest laps comparison
- Individual lap telemetry
- Tire strategy analysis
- Pit stop analysis
- Team pace comparison

### Phase 3
- Position changes visualization
- Speed analysis
- Driver consistency metrics
- Qualifying analysis

### Phase 4
- Championship scenarios
- Historical data (Ergast)
- Season summaries

## Contributing

See [COMPREHENSIVE_API_BLUEPRINT.md](./COMPREHENSIVE_API_BLUEPRINT.md) for the complete API specification.

## License

MIT License

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the comprehensive blueprint
- Check FastF1 documentation: https://docs.fastf1.dev/
