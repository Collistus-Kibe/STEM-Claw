"""Copernicus Earth Observation and Environmental dataset search tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class CopernicusDataInput(BaseModel):
    query: str = Field(..., description="Satellite mission (Sentinel-1, Sentinel-2, Sentinel-3), land cover, or climate dataset")
    collection: str = Field(default="Sentinel2", description="Copernicus collection (e.g. 'Sentinel1', 'Sentinel2', 'Sentinel3')")
    limit: int = Field(default=5, ge=1, le=15, description="Max product records to return")


class CopernicusDataTool(BaseTool):
    name = "copernicus_data"
    description = (
        "Search the Copernicus Data Space and Open Earth Observation catalog "
        "for satellite imagery granules, cloud cover %, sensing dates, and product metadata."
    )
    input_model = CopernicusDataInput

    def run(self, query: str, collection: str = "Sentinel2", limit: int = 5) -> str:
        url = f"https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/search.json"
        params = {
            "q": query,
            "maxRecords": limit,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    # Fallback to data.gov environmental dataset search if Copernicus RESTO is unreachable
                    fallback_url = "https://catalog.data.gov/api/3/action/package_search"
                    fb_resp = client.get(fallback_url, params={"q": query, "rows": limit}, headers=headers)
                    if fb_resp.status_code == 200:
                        fb_data = fb_resp.json().get("result", {})
                        packages = fb_data.get("results", [])
                        lines = [f"=== Environmental Dataset Search (Data.gov fallback, Showing: {len(packages)}) ==="]
                        for pkg in packages:
                            title = pkg.get("title", "No Title")
                            org = pkg.get("organization", {}).get("title", "Unknown Agency")
                            notes = pkg.get("notes") or ""
                            lines.append(f"\n- **{title}** [Agency: {org}]")
                            if notes:
                                lines.append(f"  Notes: {notes[:200]}...")
                        return "\n".join(lines)
                    return f"Copernicus catalog returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                features = data.get("features", [])

                if not features:
                    return f"No Copernicus {collection} products found for query '{query}'."

                lines = [f"=== Copernicus Earth Observation Products ({collection}, Showing {len(features)}) ==="]
                for feat in features:
                    props = feat.get("properties", {})
                    title = props.get("title") or feat.get("id", "Unknown Product")
                    start_date = props.get("startDate", "N/A")
                    cloud_cover = props.get("cloudCover", "N/A")
                    instrument = props.get("instrument", "N/A")
                    resolution = props.get("resolution", "N/A")
                    download_url = props.get("services", {}).get("download", {}).get("url", "")

                    lines.append(f"\n- **{title}**")
                    lines.append(f"  Acquisition Date: {start_date} | Cloud Cover: {cloud_cover}%")
                    lines.append(f"  Instrument: {instrument} | Resolution: {resolution}m")
                    if download_url:
                        lines.append(f"  Product URL: {download_url}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error querying Copernicus Data Space: {e}"

