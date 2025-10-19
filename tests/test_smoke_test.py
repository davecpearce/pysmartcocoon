#!/usr/bin/env python3
"""Test script to test async_update_data() method with debug logging."""

import asyncio
import logging
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

from pysmartcocoon import SmartCocoonManager

# Add the parent directory to the path so we can import pysmartcocoon
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")

# Set up logging to show debug output with better formatting
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_data() -> (  # pylint: disable=too-many-branches,too-many-statements,duplicate-code
    None
):
    """Test the async_update_data() method which calls all APIs internally."""
    print("=" * 60)
    print("Testing async_update_data() - Comprehensive API Test")
    print("=" * 60)
    print()

    manager = SmartCocoonManager()

    try:
        print("🔐 Step 1: Authenticating...")

        # Get credentials from environment variables
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")

        if not username or not password:
            print("❌ Missing credentials! Please set USERNAME and PASSWORD")
            print("   Example .env file:")
            print("   USERNAME=your_email@example.com")
            print("   PASSWORD=your_password")
            pytest.skip("Missing credentials")

        auth_result = await manager.async_start_services(
            username=username, password=password
        )

        if not auth_result:
            print("❌ Authentication failed!")
            pytest.fail("Authentication failed")

        print("✅ Authentication successful!")
        print()

        print("🔄 Step 2: Testing async_update_data() - calls all APIs...")
        print("   📊 Watch for detailed debug output below:")
        print("   " + "-" * 50)
        print()

        # Test the main update method that calls all APIs
        await manager.async_update_data()

        print()
        print("   " + "-" * 50)
        print("✅ async_update_data() completed!")
        print()

        # Show comprehensive results
        print("📋 Results Summary:")
        print(f"   • Locations: {len(manager.locations)} found")
        print(f"   • Rooms: {len(manager.rooms)} found")
        print(f"   • Thermostats: {len(manager.thermostats)} found")
        print(f"   • Fans: {len(manager.fans)} found")
        print()

        # Show details for each category
        if manager.locations:
            print("   🏠 Locations:")
            for location_id, location in manager.locations.items():
                print(
                    f"     - ID: {location_id}, "
                    f"Identifier: {location.identifier}"
                )
                if hasattr(location, "postal_code"):
                    print(f"       Postal Code: {location.postal_code}")

        if manager.rooms:
            print("   🏠 Rooms:")
            for room_id, room in manager.rooms.items():
                print(f"     - ID: {room_id}, Name: {room.name}")
                print(
                    f"       Temperature: {room.temperature}°C, "
                    f"Target: {room.target_temperature}°C"
                )

        if manager.thermostats:
            print("   🌡️  Thermostats:")
            for thermo_id, thermo in manager.thermostats.items():
                print(f"     - ID: {thermo_id}, Name: {thermo.name}")
                print(
                    f"       Mode: {thermo.hvac_mode}, "
                    f"State: {thermo.hvac_state}"
                )

        if manager.fans:
            print("   💨 Fans:")
            for _fan_id, fan in manager.fans.items():
                # Try to get the name from various possible sources
                fan_name = "Unknown"
                if hasattr(fan, "name"):
                    fan_name = fan.name
                elif (  # pylint: disable=protected-access
                    hasattr(fan, "_raw_data")
                    and isinstance(fan._raw_data, dict)
                    and "name" in fan._raw_data
                ):
                    fan_name = fan._raw_data["name"]
                print(f"     - ID: {fan.fan_id}, Name: {fan_name}")
                print(
                    f"       Room: {fan.room_name}, "
                    f"Connected: {fan.connected}"
                )
                print(f"       Power: {fan.power}W, Speed: {fan.speed_pct}%")

        print()
        print("=" * 60)
        print("Test completed successfully! 🎉")
        print("=" * 60)

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Test failed with error: {e}")
        import traceback  # pylint: disable=import-outside-toplevel

        traceback.print_exc()
        pytest.fail(f"Test failed with error: {e}")
    finally:
        # Clean up
        if hasattr(
            manager, "_api"
        ) and hasattr(  # pylint: disable=protected-access
            manager._api, "close"  # pylint: disable=protected-access
        ):
            await manager._api.close()  # pylint: disable=protected-access


if __name__ == "__main__":
    asyncio.run(test_update_data())
