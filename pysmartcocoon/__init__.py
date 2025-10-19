"""SmartCocoon API REST Client."""

from .api import SmartCocoonAPI
from .manager import SmartCocoonManager

__version__ = "1.4.0"
__all__ = ["SmartCocoonManager", "SmartCocoonAPI"]
