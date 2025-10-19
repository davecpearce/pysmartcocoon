#!/usr/bin/env python3
"""Monitor fan connection status to see how long it takes to update."""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from pysmartcocoon import SmartCocoonManager

# Add the parent directory to the path so we can import pysmartcocoon
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def monitor_connection_status() -> (
    None
):  # pylint: disable=too-many-branches,too-many-statements
    """Monitor fan connection status over time."""
    print("=" * 80)
    print("🔌 Fan Connection Status Monitor")
    print("=" * 80)
    print()

    # Get credentials from environment variables
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        print(
            "❌ Missing credentials! Please set USERNAME and PASSWORD in .env"
        )
        return

    manager = SmartCocoonManager()

    try:
        print("🔐 Authenticating...")
        auth_result = await manager.async_start_services(
            username=username, password=password
        )

        if not auth_result:
            print("❌ Authentication failed!")
            return

        print("✅ Authentication successful!")
        print()

        # Get initial data
        print("📊 Getting initial fan data...")
        await manager.async_update_data()

        if not manager.fans:
            print("❌ No fans found!")
            return

        print(f"✅ Found {len(manager.fans)} fans")
        print()

        # Show initial status
        print("🔍 Initial Connection Status:")
        print("-" * 50)
        for fan_id, fan in manager.fans.items():
            last_conn = fan.last_connection
            if last_conn:
                time_since = datetime.now(last_conn.tzinfo) - last_conn
                time_str = str(time_since).split(".", maxsplit=1)[
                    0
                ]  # Remove microseconds
            else:
                time_str = "Unknown"

            print(f"  Fan {fan_id}:")
            print(f"    Connected: {fan.connected}")
            print(f"    Last Connection: {last_conn}")
            print(f"    Time Since: {time_str}")
            print()

        print("⏰ Starting monitoring loop...")
        print("   Press Ctrl+C to stop")
        print("-" * 50)

        # Monitor loop
        start_time = datetime.now()
        check_count = 0

        while True:
            check_count += 1
            current_time = datetime.now()
            elapsed = current_time - start_time

            print(
                f"\n🔄 Check #{check_count} - "
                f"Elapsed: {str(elapsed).split('.', maxsplit=1)[0]}"
            )

            # Update data
            await manager.async_update_data()

            # Show status for each fan
            for fan_id, fan in manager.fans.items():
                last_conn = fan.last_connection
                if last_conn:
                    time_since = current_time - last_conn.replace(tzinfo=None)
                    time_str = str(time_since).split(".", maxsplit=1)[0]
                else:
                    time_str = "Unknown"

                status_icon = "🟢" if fan.connected else "🔴"
                print(
                    f"  {status_icon} Fan {fan_id}: "
                    f"Connected={fan.connected}, Last seen: {time_str}"
                )

            # Wait 30 seconds before next check
            print("   ⏳ Waiting 30 seconds...")
            await asyncio.sleep(30)

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Clean up
        if hasattr(
            manager, "_api"
        ) and hasattr(  # pylint: disable=protected-access
            manager._api, "close"  # pylint: disable=protected-access
        ):
            await manager._api.close()  # pylint: disable=protected-access


if __name__ == "__main__":
    asyncio.run(monitor_connection_status())
