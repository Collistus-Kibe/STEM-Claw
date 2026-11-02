"""NASA Images & Media API search tool for Earth and space observation data."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class NASAMediaSearchInput(BaseModel):
    query: str = Field(..., description="Earth observation mission, satellite instrument, nebula, or planetary query")
    media_type: str = Field(default="image", description="'image', 'video', or 'audio'")
    limit: int = Field(default=5, ge=1, le=15, description="Max media records to return")


class NASAMediaSearchTool(BaseTool):
    name = "nasa_media_search"
    description = (
        "Search the NASA Images and Media Library for Earth observation imagery, "
        "satellite remote sensing captures, mission data, and astronomical surveys."
    )
    input_model = NASAMediaSearchInput

    def run(self, query: str, media_type: str = "image", limit: int = 5) -> str:
        url = "https://images-api.nasa.gov/search"
        params = {
            "q": query,
            "media_type": media_type,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"NASA Media API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                collection = data.get("collection", {})
                metadata = collection.get("metadata", {})
                total = metadata.get("total_hits", 0)
                items = collection.get("items", [])[:limit]

                if not items:
                    return f"No NASA media found for query '{query}'."

                lines = [f"=== NASA Media Library Search (Total Hits: {total:,}, Showing: {len(items)}) ==="]
                for item in items:
                    item_data = (item.get("data") or [{}])[0]
                    nasa_id = item_data.get("nasa_id", "")
                    title = item_data.get("title", "No Title")
                    date_created = item_data.get("date_created", "N/A")[:10]
                    center = item_data.get("center", "NASA")
                    keywords = item_data.get("keywords", [])
                    kw_str = ", ".join(keywords[:5]) if keywords else "None"
                    desc = item_data.get("description") or "No description available."
                    if len(desc) > 250:
                        desc = desc[:247] + "..."

                    # Image preview link
                    links = item.get("links", [])
                    preview_href = links[0].get("href", "") if links else ""

                    lines.append(f"\n- **{title}** ({date_created}) [Center: {center}]")
                    lines.append(f"  NASA ID: {nasa_id}")
                    lines.append(f"  Keywords: {kw_str}")
                    lines.append(f"  Description: {desc}")
                    if preview_href:
                        lines.append(f"  Preview Asset: {preview_href}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing NASA Media search: {e}"

