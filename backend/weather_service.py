"""
OpenWeatherMap forecast helper for trip date ranges.
Uses the free 5-day / 3-hour forecast API (about 5 calendar days from request time).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

from backend.config import WEATHER_API_KEY

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def _require_key() -> str | None:
    if not WEATHER_API_KEY or not WEATHER_API_KEY.strip():
        return None
    return WEATHER_API_KEY.strip()


def geocode_destination(query: str) -> tuple[float, float, str] | None:
    """Resolve a place name to (lat, lon, display_name)."""
    key = _require_key()
    if not key or not query or not query.strip():
        return None
    try:
        r = requests.get(
            GEOCODE_URL,
            params={"q": query.strip(), "limit": 1, "appid": key},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        row = data[0]
        name = row.get("name", query.strip())
        country = row.get("country", "")
        state = row.get("state", "")
        label = f"{name}, {state}, {country}".replace(", , ", ", ").strip(", ")
        return float(row["lat"]), float(row["lon"]), label
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None


def _aggregate_day(entries: list[dict[str, Any]]) -> dict[str, Any]:
    temps = [e["main"]["temp"] for e in entries if "main" in e]
    pops = [e.get("pop", 0) or 0 for e in entries]
    descs = []
    for e in entries:
        w = e.get("weather") or []
        if w and isinstance(w[0], dict):
            descs.append(w[0].get("description", "").strip())
    dominant = max(set(descs), key=descs.count) if descs else "n/a"
    return {
        "temp_min": min(temps) if temps else None,
        "temp_max": max(temps) if temps else None,
        "pop_max": max(pops) if pops else None,
        "summary": dominant,
    }


def fetch_forecast_payload(lat: float, lon: float) -> dict[str, Any] | None:
    key = _require_key()
    if not key:
        return None
    try:
        r = requests.get(
            FORECAST_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": key,
                "units": "metric",
            },
            timeout=20,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None


def build_trip_weather_report(
    destination_query: str,
    trip_start: date,
    trip_end: date,
) -> tuple[str, str | None]:
    """
    Returns (markdown_for_ui_and_agent, error_message_or_none).
    """
    if trip_end < trip_start:
        return "", "End date cannot be before start date."

    geo = geocode_destination(destination_query)
    if not geo:
        key = _require_key()
        if not key:
            return (
                "*Weather: API key not configured. Add `WEATHER_API_KEY` to your `.env` file.*",
                None,
            )
        return "", f"Could not find coordinates for “{destination_query.strip()}”. Try a clearer city or region name."

    lat, lon, place_label = geo
    payload = fetch_forecast_payload(lat, lon)
    if not payload or "list" not in payload:
        return "", "Weather service temporarily unavailable. Please try again later."

    by_day: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for item in payload["list"]:
        ts = item.get("dt")
        if ts is None:
            continue
        d = datetime.fromtimestamp(int(ts), tz=timezone.utc).date()
        by_day[d].append(item)

    if not by_day:
        return "", "No forecast intervals returned for this location."

    api_first = min(by_day.keys())
    api_last = max(by_day.keys())

    lines = [
        f"**Destination (forecast location):** {place_label}",
        "",
        f"**Trip window:** {trip_start.isoformat()} → {trip_end.isoformat()} (UTC calendar days for forecast samples)",
        "",
    ]

    covered: list[date] = []
    d = trip_start
    while d <= trip_end:
        if d in by_day:
            covered.append(d)
        d += timedelta(days=1)

    if not covered:
        lines.append(
            "*No hourly forecast samples fall on your trip dates.* "
            "The free OpenWeather **5-day forecast** only reaches about "
            f"**{api_first}** through **{api_last}**. "
            "Choose trip dates inside that window, or wait until your trip is closer."
        )
        summary = "\n".join(lines)
        return summary, None

    lines.append("| Date | Low (°C) | High (°C) | Rain chance | Conditions |")
    lines.append("| --- | ---: | ---: | ---: | --- |")

    for d in sorted(covered):
        agg = _aggregate_day(by_day[d])
        tmin = f"{agg['temp_min']:.0f}" if agg["temp_min"] is not None else "—"
        tmax = f"{agg['temp_max']:.0f}" if agg["temp_max"] is not None else "—"
        pop = f"{int(round((agg['pop_max'] or 0) * 100))}%" if agg["pop_max"] is not None else "—"
        lines.append(f"| {d.isoformat()} | {tmin} | {tmax} | {pop} | {agg['summary']} |")

    if trip_start < api_first or trip_end > api_last:
        lines.append("")
        lines.append(
            f"*Note: Forecast API coverage is roughly **{api_first}**–**{api_last}**. "
            "Days outside that range are omitted.*"
        )

    if trip_start < date.today():
        lines.append("")
        lines.append(
            "*Past dates: this endpoint is a **forecast**, not historical weather; "
            "rows above only appear if the API still returned samples for those days.*"
        )

    summary = "\n".join(lines)
    return summary, None


def compact_weather_for_prompt(markdown_report: str, max_chars: int = 3500) -> str:
    """Trim very long markdown for LLM context."""
    t = markdown_report.strip()
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 20] + "\n…(truncated)"
