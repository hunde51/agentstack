"""Tool implementations: SQLite users + Open-Meteo weather (no API key)."""

from typing import Any

import httpx

from .db import get_all_users


def get_users() -> list[dict[str, Any]]:
    return get_all_users()


def _geocode_city(city: str) -> tuple[float, float] | None:
    city = city.strip()
    if not city:
        return None
    try:
        r = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results") or []
        if not results:
            return None
        lat = results[0].get("latitude")
        lon = results[0].get("longitude")
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return None


def get_weather(city: str) -> dict[str, Any]:
    coords = _geocode_city(city)
    if coords is None:
        return {
            "city": city.strip() or "unknown",
            "error": "City not found",
            "forecast": None,
            "temperature_c": None,
        }
    lat, lon = coords
    try:
        r = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
            },
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json()
        cw = data.get("current_weather") or {}
        temp = cw.get("temperature")
        code = cw.get("weathercode")
        # WMO code rough label (simplified)
        forecast = _wmo_label(code) if code is not None else "unknown"
        return {
            "city": city.strip(),
            "forecast": forecast,
            "temperature_c": float(temp) if temp is not None else None,
            "latitude": lat,
            "longitude": lon,
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        return {
            "city": city.strip(),
            "error": f"Weather request failed: {exc}",
            "forecast": None,
            "temperature_c": None,
        }


def _wmo_label(code: int) -> str:
    # Simplified WMO weathercode mapping for Open-Meteo (labels align with UI cards)
    if code == 0:
        return "sunny"
    if code in (1, 2, 3):
        return "partly cloudy"
    if code in (45, 48):
        return "foggy"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 80, 81, 82):
        return "rainy"
    if code in (71, 73, 75, 77, 85, 86):
        return "snowy"
    if code in (95, 96, 99):
        return "stormy"
    return "cloudy"
