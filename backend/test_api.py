"""
Quick API test script
Run this after starting the server to verify all endpoints work
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def print_response(name: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response preview:")
        print(json.dumps(data, indent=2)[:500])  # First 500 chars
        print("✅ PASSED")
    else:
        print(f"Error: {response.text}")
        print("❌ FAILED")


def test_health():
    """Test health check"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_seasons():
    """Test seasons endpoint"""
    response = requests.get(f"{API_V1}/seasons")
    print_response("Get Seasons", response)
    return response.status_code == 200


def test_events(year: int = 2024):
    """Test events endpoint"""
    response = requests.get(f"{API_V1}/events/{year}")
    print_response(f"Get Events for {year}", response)

    if response.status_code == 200:
        events = response.json()["events"]
        print(f"\nFound {len(events)} events")
        if events:
            first_event = events[0]
            print(f"First event: {first_event['event_name']} at {first_event['location']}")
            return True, first_event["event_name"]

    return False, None


def test_sessions(year: int = 2024, event: str = "Bahrain"):
    """Test sessions endpoint"""
    response = requests.get(f"{API_V1}/events/{year}/{event}/sessions")
    print_response(f"Get Sessions for {year} {event}", response)

    if response.status_code == 200:
        sessions = response.json()["sessions"]
        print(f"\nFound {len(sessions)} sessions")
        return True
    return False


def test_drivers(year: int = 2024, event: str = "Bahrain", session: str = "R"):
    """Test drivers endpoint"""
    response = requests.get(f"{API_V1}/sessions/{year}/{event}/{session}/drivers")
    print_response(f"Get Drivers for {year} {event} {session}", response)

    if response.status_code == 200:
        drivers = response.json()["drivers"]
        print(f"\nFound {len(drivers)} drivers")
        if len(drivers) >= 2:
            driver1 = drivers[0]["abbreviation"]
            driver2 = drivers[1]["abbreviation"]
            return True, driver1, driver2
    return False, None, None


def test_results(year: int = 2024, event: str = "Bahrain", session: str = "R"):
    """Test session results endpoint"""
    response = requests.get(f"{API_V1}/sessions/{year}/{event}/{session}/results")
    print_response(f"Get Results for {year} {event} {session}", response)
    return response.status_code == 200


def test_laps(year: int = 2024, event: str = "Bahrain", session: str = "R", driver: str = None):
    """Test laps endpoint"""
    url = f"{API_V1}/sessions/{year}/{event}/{session}/laps"
    params = {"limit": 10}
    if driver:
        params["driver"] = driver

    response = requests.get(url, params=params)
    print_response(f"Get Laps for {year} {event} {session}", response)

    if response.status_code == 200:
        laps_data = response.json()
        print(f"\nTotal laps: {laps_data['total_laps']}")
    return response.status_code == 200


def test_telemetry_comparison(year: int, event: str, session: str, driver1: str, driver2: str):
    """Test telemetry comparison endpoint (CORE FEATURE)"""
    params = {
        "year": year,
        "event": event,
        "session_type": session,
        "driver1": driver1,
        "driver2": driver2
    }

    print(f"\n🏎️  Comparing {driver1} vs {driver2}")
    response = requests.get(f"{API_V1}/telemetry/compare", params=params)
    print_response(f"Compare Telemetry: {driver1} vs {driver2}", response)

    if response.status_code == 200:
        data = response.json()
        print(f"\nData points: {data['data_points']}")
        print(f"Lap time delta: {data['lap_time_delta']:.3f}s")
        print(f"Max speed delta: {data['max_speed_delta']:.1f} km/h")
    return response.status_code == 200


def test_circuit(year: int = 2024, event: str = "Monaco"):
    """Test circuit endpoint"""
    response = requests.get(f"{API_V1}/circuit/{year}/{event}")
    print_response(f"Get Circuit for {year} {event}", response)

    if response.status_code == 200:
        data = response.json()
        print(f"\nCircuit: {data.get('circuit_name', 'Unknown')}")
        print(f"Corners: {len(data.get('corners', []))}")
        print(f"Track points: {len(data['track_map']['x_coordinates'])}")
    return response.status_code == 200


def test_weather(year: int = 2024, event: str = "Bahrain", session: str = "R"):
    """Test weather endpoint"""
    response = requests.get(f"{API_V1}/weather/{year}/{event}/{session}")
    print_response(f"Get Weather for {year} {event} {session}", response)

    if response.status_code == 200:
        data = response.json()
        print(f"\nWeather data points: {len(data['weather_data'])}")
        summary = data['summary']
        print(f"Avg air temp: {summary['avg_air_temp']:.1f}°C")
        print(f"Rain detected: {summary['rain_detected']}")
    return response.status_code == 200


def test_team_colors(year: int = 2024):
    """Test team colors endpoint"""
    response = requests.get(f"{API_V1}/visualization/team-colors/{year}")
    print_response(f"Get Team Colors for {year}", response)

    if response.status_code == 200:
        data = response.json()
        print(f"\nTeams: {len(data['teams'])}")
    return response.status_code == 200


def test_compound_colors():
    """Test compound colors endpoint"""
    response = requests.get(f"{API_V1}/visualization/compound-colors")
    print_response("Get Compound Colors", response)

    if response.status_code == 200:
        data = response.json()
        compounds = data['compounds']
        print(f"\nCompounds: {[c['name'] for c in compounds]}")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║       F1 Telemetry API - Phase 1 Test Suite             ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print(f"Testing API at: {BASE_URL}")
    print("Make sure the server is running: uvicorn app.main:app --reload")

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health()))

    # Test 2: Seasons
    results.append(("Seasons", test_seasons()))

    # Test 3: Events
    success, event_name = test_events(2024)
    results.append(("Events", success))

    if not event_name:
        event_name = "Bahrain"

    # Test 4: Sessions
    results.append(("Sessions", test_sessions(2024, event_name)))

    # Test 5: Drivers
    success, driver1, driver2 = test_drivers(2024, event_name, "R")
    results.append(("Drivers", success))

    if not driver1:
        driver1, driver2 = "VER", "HAM"

    # Test 6: Results
    results.append(("Session Results", test_results(2024, event_name, "R")))

    # Test 7: Laps
    results.append(("Laps", test_laps(2024, event_name, "R", driver1)))

    # Test 8: Telemetry Comparison (CORE FEATURE)
    results.append(("Telemetry Comparison", test_telemetry_comparison(
        2024, event_name, "Q", driver1, driver2
    )))

    # Test 9: Circuit
    results.append(("Circuit Info", test_circuit(2024, "Monaco")))

    # Test 10: Weather
    results.append(("Weather Data", test_weather(2024, event_name, "R")))

    # Test 11: Team Colors
    results.append(("Team Colors", test_team_colors(2024)))

    # Test 12: Compound Colors
    results.append(("Compound Colors", test_compound_colors()))

    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<40} {status}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Backend is ready!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")


if __name__ == "__main__":
    main()
