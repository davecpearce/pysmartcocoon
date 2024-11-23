"""SmartCocoon constants."""

from enum import Enum

# API Data
API_URL = "https://app.mysmartcocoon.com/api/"
API_AUTH_URL = API_URL + "auth/sign_in"
API_FANS_URL = API_URL + "fans/"
API_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "SmartCocoon/12601 CFNetwork/1568.300.101 Darwin/24.2.0",
}

# Default fan speed is 38% in the SmartCocoon app
# but 33% works better for HomeAssistant
DEFAULT_FAN_POWER_PCT = 33

DEFAULT_TIMEOUT: int = 30


class EntityType(Enum):
    """Class to define entity types"""

    # SmartCocoon entity types

    LOCATIONS = "client_systems"
    THERMOSTATS = "thermostats"
    ROOMS = "rooms"
    FANS = "fans"


class FanMode(Enum):
    """Fan mode."""

    ECO = "eco"
    OFF = "always_off"
    ON = "always_on"
    AUTO = "auto"


class FanState(Enum):
    """Fan State."""

    FAN_OFF = "false"
    FAN_ON = "true"
