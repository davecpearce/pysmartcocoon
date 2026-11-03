"""SmartCocoon API REST Client."""

from .api import SmartCocoonAPI
from .manager import SmartCocoonManager

__version__ = "1.6.0"
__all__ = ["SmartCocoonManager", "SmartCocoonAPI"]
