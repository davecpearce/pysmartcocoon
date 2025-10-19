#!/usr/bin/env python3
"""Test the extra state attributes functionality."""

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

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@pytest.mark.asyncio
@pytest.mark.integration  # pylint: disable=unknown-option-value
async def test_extra_attributes() -> None:  # pylint: disable=duplicate-code
    """Test the extra state attributes functionality."""
    print("=" * 80)
    print("🔍 Testing Extra State Attributes")
    print("=" * 80)
    print()

    # Get credentials from environment variables
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        print(
            "❌ Missing credentials! Please set USERNAME and PASSWORD in .env"
        )
        pytest.skip("Missing credentials")

    manager = SmartCocoonManager()

    try:
        print("🔐 Authenticating...")
        auth_result = await manager.async_start_services(
            username=username, password=password
        )

        if not auth_result:
            print("❌ Authentication failed!")
            pytest.fail("Authentication failed")

        print("✅ Authentication successful!")
        print()

        # Get fan data
        print("📊 Getting fan data...")
        await manager.async_update_data()

        if not manager.fans:
            print("❌ No fans found!")
            pytest.fail("No fans found")

        print(f"✅ Found {len(manager.fans)} fans")
        print()

        # Test extra attributes for each fan
        for fan_id, fan in manager.fans.items():
            print(f"🔍 Fan {fan_id} Extra Attributes:")
            print("-" * 50)

            attributes = fan.get_extra_state_attributes()

            for key, value in attributes.items():
                print(f"  {key}: {value}")

            print()

        print("=" * 80)
        print("✅ Extra attributes test completed!")
        print("=" * 80)

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\n❌ Error: {e}")
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
    asyncio.run(test_extra_attributes())
