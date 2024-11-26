"""Global variables used across the application."""

from typing import Literal

platform: Literal["telegram", "web"] = ""
user_location: dict[str, float] = {"latitude": None, "longitude": None}
