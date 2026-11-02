"""USGS Earthquake and seismic event API query tool."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class USGSEarthquakesInput(BaseModel):
    min_magnitude: float = Field(default=4.5, ge=1.0, le=10.0, description="Minimum earthquake magnitude (Richter scale)")
    limit: int = Field(default=8, ge=1, le=30, description="Max seismic events to return")
    days_back: int = Field(default=30, ge=1, le=365, description="Number of days back to search")


class USGSEarthquakesTool(BaseTool):
    name = "usgs_earthquakes"
    description = (
        "Query the USGS Earthquake Hazards API for real-time seismic events, magnitude, "
        "hypocenter depth, geographic coordinates, tsunami warnings, and USGS event pages."
    )
    input_model = USGSEarthquakesInput

    def run(self, min_magnitude: float = 4.5, limit: int = 8, days_back: int = 30) -> str:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "minmagnitude": min_magnitude,
            "limit": limit,
            "orderby": "time",
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"USGS API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                metadata = data.get("metadata", {})
                total = metadata.get("count", 0)
                features = data.get("features", [])

                if not features:
                    return f"No USGS earthquake events found with magnitude >= {min_magnitude}."

                lines = [f"=== USGS Seismic Events (Min Mag: {min_magnitude}, Found: {total}, Showing: {len(features)}) ==="]
                for feat in features:
                    props = feat.get("properties", {})
                    geom = feat.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0, 0])
                    lon, lat, depth_km = coords[0], coords[1], coords[2]

                    place = props.get("place", "Unknown Location")
                    mag = props.get("mag", "N/A")
                    time_epoch = props.get("time", 0) / 1000.0
                    event_dt = datetime.fromtimestamp(time_epoch, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    tsunami = "YES" if props.get("tsunami") == 1 else "No"
                    url_link = props.get("url", "")

                    lines.append(f"\n- **M {mag}** - {place}")
                    lines.append(f"  Time: {event_dt}")
                    lines.append(f"  Coordinates: ({lat}, {lon}) | Hypocenter Depth: {depth_km} km")
                    lines.append(f"  Tsunami Flag: {tsunami} | Event Details: {url_link}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing USGS earthquake query: {e}"

