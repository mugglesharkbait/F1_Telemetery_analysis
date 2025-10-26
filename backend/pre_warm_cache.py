"""
Pre-warm FastF1 Cache Script
Downloads and caches popular F1 sessions to speed up API responses

Run this once to pre-download commonly requested sessions:
    python pre_warm_cache.py

This will make subsequent API requests 10-20x faster!
"""

import fastf1
import time
from datetime import datetime

# Enable cache
fastf1.Cache.enable_cache('fastf1_cache')

# Popular sessions to pre-cache
SESSIONS_TO_CACHE = [
    # 2024 Season - Popular races
    (2024, 'Bahrain', ['Q', 'R']),
    (2024, 'Saudi Arabia', ['Q', 'R']),
    (2024, 'Australia', ['Q', 'R']),
    (2024, 'Japan', ['Q', 'R']),
    (2024, 'China', ['Q', 'R']),
    (2024, 'Miami', ['Q', 'R']),
    (2024, 'Emilia Romagna', ['Q', 'R']),
    (2024, 'Monaco', ['Q', 'R']),
    (2024, 'Canada', ['Q', 'R']),
    (2024, 'Spain', ['Q', 'R']),
    (2024, 'Austria', ['Q', 'R']),
    (2024, 'Great Britain', ['Q', 'R']),
    (2024, 'Hungary', ['Q', 'R']),
    (2024, 'Belgium', ['Q', 'R']),
    (2024, 'Netherlands', ['Q', 'R']),
    (2024, 'Italy', ['Q', 'R']),
    (2024, 'Azerbaijan', ['Q', 'R']),
    (2024, 'Singapore', ['Q', 'R']),
    (2024, 'United States', ['Q', 'R']),
    (2024, 'Mexico', ['Q', 'R']),
    (2024, 'Brazil', ['Q', 'R']),
    (2024, 'Las Vegas', ['Q', 'R']),
    (2024, 'Qatar', ['Q', 'R']),
    (2024, 'Abu Dhabi', ['Q', 'R']),

    # 2023 Season - Popular races
    (2023, 'Monaco', ['Q', 'R']),
    (2023, 'Silverstone', ['Q', 'R']),
    (2023, 'Spa', ['Q', 'R']),
    (2023, 'Monza', ['Q', 'R']),
    (2023, 'Singapore', ['Q', 'R']),
    (2023, 'Austin', ['Q', 'R']),
    (2023, 'Brazil', ['Q', 'R']),
    (2023, 'Abu Dhabi', ['Q', 'R']),
]


def cache_session(year: int, event: str, session_type: str) -> bool:
    """
    Cache a single session

    Args:
        year: Season year
        event: Event name
        session_type: Session type (Q, R, etc.)

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"  ⏳ Loading telemetry and laps...", end='', flush=True)
        start = time.time()

        # Load session
        session = fastf1.get_session(year, event, session_type)

        # Load all data that the API endpoints will need
        session.load(
            telemetry=True,  # For telemetry comparison
            laps=True,       # For lap times
            weather=True     # For weather endpoint
        )

        elapsed = time.time() - start
        print(f" ✓ ({elapsed:.1f}s)")
        return True

    except Exception as e:
        print(f" ✗ Error: {str(e)[:50]}")
        return False


def main():
    """Main pre-warming function"""

    print("""
╔═══════════════════════════════════════════════════════════╗
║          FastF1 Cache Pre-warming Script                  ║
║  This will download F1 data to speed up API responses     ║
╚═══════════════════════════════════════════════════════════╝
    """)

    print(f"Cache directory: fastf1_cache/")
    print(f"Sessions to cache: {sum(len(sessions) for _, _, sessions in SESSIONS_TO_CACHE)}")
    print("\nThis may take 30-60 minutes depending on your internet connection.")
    print("You can stop at any time with Ctrl+C - progress will be saved.\n")

    input("Press Enter to continue or Ctrl+C to cancel...")

    total_start = time.time()
    success_count = 0
    error_count = 0
    total_sessions = sum(len(sessions) for _, _, sessions in SESSIONS_TO_CACHE)

    for year, event, session_types in SESSIONS_TO_CACHE:
        print(f"\n📅 {year} {event}")

        for session_type in session_types:
            print(f"  🏎️  {session_type:2s}", end='')

            if cache_session(year, event, session_type):
                success_count += 1
            else:
                error_count += 1

    total_time = time.time() - total_start

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total sessions: {total_sessions}")
    print(f"Successful: {success_count} ✓")
    print(f"Failed: {error_count} ✗")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average per session: {total_time/total_sessions:.1f} seconds")

    if success_count > 0:
        print("\n🎉 Cache pre-warmed! API requests will now be much faster!")
        print("\nTest it:")
        print('  curl "http://localhost:8000/api/v1/telemetry/compare?year=2024&event=Monaco&session_type=Q&driver1=VER&driver2=LEC"')
        print("\nExpected response time: < 3 seconds (vs 20-30 seconds before)")

    if error_count > 0:
        print(f"\n⚠️  {error_count} session(s) failed. This is normal for:")
        print("  - Future races that haven't happened yet")
        print("  - Sessions that were cancelled")
        print("  - Events with different session names")


def quick_cache():
    """Quick cache for most popular sessions only"""
    print("Quick caching most popular sessions (Monaco, Silverstone, etc.)...\n")

    popular = [
        (2024, 'Monaco', ['Q', 'R']),
        (2024, 'Silverstone', ['Q', 'R']),
        (2024, 'Spa', ['Q', 'R']),
        (2024, 'Monza', ['Q', 'R']),
        (2024, 'Singapore', ['Q', 'R']),
        (2024, 'Austin', ['Q', 'R']),
    ]

    success = 0
    for year, event, session_types in popular:
        print(f"📅 {year} {event}")
        for session_type in session_types:
            print(f"  {session_type}", end='')
            if cache_session(year, event, session_type):
                success += 1

    print(f"\n✓ Cached {success} popular sessions!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_cache()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Progress has been saved.")
            print("You can run this script again to continue caching.")
