"""Tool implementations: SQLite users, Open-Meteo weather, and recent web/news lookups."""

import os
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree

import httpx

from .db import get_all_users


def get_users() -> list[dict[str, Any]]:
    return get_all_users()


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _max_recent_results() -> int:
    raw = os.getenv("RECENT_INFO_MAX_RESULTS", "5").strip()
    try:
        return max(1, min(int(raw), 10))
    except ValueError:
        return 5


def _google_news_search(query: str, *, limit: int) -> list[dict[str, Any]]:
    response = httpx.get(
        "https://news.google.com/rss/search",
        params={
            "q": query,
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        },
        headers={"User-Agent": "agentstack/1.0"},
        timeout=10.0,
        follow_redirects=True,
    )
    response.raise_for_status()

    root = ElementTree.fromstring(response.text)
    items: list[dict[str, Any]] = []

    for item in root.findall("./channel/item"):
        title = _clean_text(item.findtext("title"))
        link = _clean_text(item.findtext("link"))
        source = _clean_text(item.findtext("source"))
        published = _clean_text(item.findtext("pubDate"))

        if not title or not link:
            continue

        published_iso: str | None = None
        if published:
            try:
                published_iso = (
                    parsedate_to_datetime(published)
                    .astimezone(UTC)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
            except (TypeError, ValueError, IndexError, OverflowError):
                published_iso = None

        items.append(
            {
                "title": title,
                "link": link,
                "source": source or None,
                "published_at": published_iso,
            }
        )
        if len(items) >= limit:
            break

    return items


def _duckduckgo_instant_answer(query: str) -> dict[str, Any] | None:
    response = httpx.get(
        "https://api.duckduckgo.com/",
        params={
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        },
        headers={"User-Agent": "agentstack/1.0"},
        timeout=10.0,
    )
    response.raise_for_status()

    data = response.json()
    summary = _clean_text(data.get("AbstractText"))
    url = _clean_text(data.get("AbstractURL"))
    heading = _clean_text(data.get("Heading"))

    if not summary and not url and not heading:
        return None

    return {
        "heading": heading or None,
        "summary": summary or None,
        "url": url or None,
    }


def search_recent_info(query: str) -> dict[str, Any]:
    cleaned_query = _clean_text(query)
    if not cleaned_query:
        return {
            "query": "",
            "as_of": _utc_now_iso(),
            "error": "Query must not be empty",
            "results": [],
        }

    limit = _max_recent_results()
    payload: dict[str, Any] = {
        "query": cleaned_query,
        "as_of": _utc_now_iso(),
        "results": [],
        "instant_answer": None,
    }

    errors: list[str] = []

    try:
        payload["results"] = _google_news_search(cleaned_query, limit=limit)
    except (httpx.HTTPError, ElementTree.ParseError, ValueError) as exc:
        errors.append(f"Google News search failed: {exc}")

    try:
        payload["instant_answer"] = _duckduckgo_instant_answer(cleaned_query)
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        errors.append(f"DuckDuckGo instant answer failed: {exc}")

    if errors and not payload["results"] and payload["instant_answer"] is None:
        payload["error"] = "; ".join(errors)

    return payload


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
