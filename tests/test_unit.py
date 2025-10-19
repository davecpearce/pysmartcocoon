#!/usr/bin/env python3
"""Unit tests that don't require real API calls."""

from pysmartcocoon import SmartCocoonAPI, SmartCocoonManager
from pysmartcocoon.const import API_AUTH_URL, API_URL


def test_constants() -> None:
    """Test that constants are properly defined."""
    assert API_URL == "https://app.mysmartcocoon.com/api/"
    assert API_AUTH_URL == "https://app.mysmartcocoon.com/api/auth/sign_in"


def test_imports() -> None:
    """Test that main classes can be imported."""
    # Test that classes are importable
    assert SmartCocoonAPI is not None
    assert SmartCocoonManager is not None


def test_basic_functionality() -> None:
    """Test basic functionality without API calls."""

    # Create manager instance
    manager = SmartCocoonManager()

    # Test that properties exist
    assert hasattr(manager, "locations")
    assert hasattr(manager, "thermostats")
    assert hasattr(manager, "rooms")
    assert hasattr(manager, "fans")

    # Test that properties return empty dicts initially
    assert not manager.locations
    assert not manager.thermostats
    assert not manager.rooms
    assert not manager.fans
