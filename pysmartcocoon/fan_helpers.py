"""Helper functions for fan mode and speed logic."""

from __future__ import annotations

from pysmartcocoon.const import DEFAULT_FAN_POWER_PCT, FanMode


def derive_mode_from_speed(
    current_mode: FanMode, fan_speed_pct: int | None
) -> FanMode:
    """Derive the target mode from a desired speed and the current mode."""
    if fan_speed_pct == 0:
        return FanMode.OFF if current_mode == FanMode.ON else current_mode
    return FanMode.ON if current_mode == FanMode.OFF else current_mode


def resolve_speed(
    current_speed_pct: int,
    fan_mode: FanMode,
    fan_speed_pct: int | None,
) -> int | None:
    """Resolve a valid speed (0-100).

    Returns None if invalid input provided.
    """
    if fan_speed_pct is None:
        if fan_mode == FanMode.OFF:
            return current_speed_pct
        if fan_mode == FanMode.ON and current_speed_pct == 0:
            return DEFAULT_FAN_POWER_PCT
        return current_speed_pct
    if fan_speed_pct < 0 or fan_speed_pct > 100:
        return None
    return fan_speed_pct
