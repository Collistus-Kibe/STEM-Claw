"""Zenodo open science repository search tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class ZenodoSearchInput(BaseModel):
    query: str = Field(..., description="Research dataset keyword, software title, open data archive, or author")
    limit: int = Field(default=5, ge=1, le=15, description="Max Zenodo records to return")


class ZenodoSearchTool(BaseTool):
    name = "zenodo_search"
    description = (
        "Search CERN's Zenodo open science repository for open datasets, research software, "
        "supplementary materials, posters, and replication packages."
    )
    input_model = ZenodoSearchInput

    def run(self, query: str, limit: int = 5) -> str:
        url = "https://zenodo.org/api/records"
        params = {
            "q": query,
            "size": limit,
            "sort": "bestmatch",
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"Zenodo API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                hits = data.get("hits", {})
                total = hits.get("total", 0)
                records = hits.get("hits", [])

                if not records:
                    return f"No Zenodo records found for query '{query}'."

                lines = [f"=== Zenodo Open Science Repository (Total Found: {total:,}, Showing: {len(records)}) ==="]
                for rec in records:
                    metadata = rec.get("metadata", {})
                    title = metadata.get("title", "No Title")
                    pub_date = metadata.get("publication_date", "N/A")
                    res_type = metadata.get("resource_type", {}).get("title", "Dataset/Publication")
                    doi = metadata.get("doi", "") or rec.get("doi", "")
                    license_str = metadata.get("license", {}).get("id", "Open")
                    record_url = rec.get("links", {}).get("html", f"https://zenodo.org/record/{rec.get('id', '')}")

                    creators = [c.get("name", "") for c in metadata.get("creators", []) if c.get("name")]
                    creators_str = ", ".join(creators[:3])

                    lines.append(f"\n- **{title}** ({pub_date}) [Type: {res_type}]")
                    if creators_str:
                        lines.append(f"  Creators: {creators_str}")
                    if doi:
                        lines.append(f"  DOI: https://doi.org/{doi}")
                    lines.append(f"  License: {license_str} | URL: {record_url}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing Zenodo search: {e}"

