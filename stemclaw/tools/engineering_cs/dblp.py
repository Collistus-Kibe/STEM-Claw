"""DBLP Computer Science Bibliography search tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class DBLPSearchInput(BaseModel):
    query: str = Field(..., description="Computer science author, topic, or conference paper title")
    limit: int = Field(default=8, ge=1, le=30, description="Maximum number of publication hits to return")


class DBLPSearchTool(BaseTool):
    name = "dblp_search"
    description = (
        "Search the DBLP Computer Science Bibliography for peer-reviewed papers, "
        "conference proceedings, journal articles, and computer science authors."
    )
    input_model = DBLPSearchInput

    def run(self, query: str, limit: int = 8) -> str:
        url = "https://dblp.org/search/publ/api"
        params = {
            "q": query,
            "format": "json",
            "h": limit,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"DBLP API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                result_obj = data.get("result", {})
                hits_obj = result_obj.get("hits", {})
                total = hits_obj.get("@total", "0")
                hit_list = hits_obj.get("hit", [])

                if not hit_list:
                    return f"No DBLP publications found for query '{query}'."

                lines = [f"=== DBLP Search Results (Total Hits: {total}, Showing: {len(hit_list)}) ==="]
                for hit in hit_list:
                    info = hit.get("info", {})
                    title = info.get("title", "No Title").rstrip(".")
                    venue = info.get("venue", "Unknown Venue")
                    year = info.get("year", "N/A")
                    pub_type = info.get("type", "Publication")
                    ee = info.get("ee", "")
                    url_link = info.get("url", "")

                    authors_data = info.get("authors", {}).get("author", [])
                    if isinstance(authors_data, list):
                        authors = ", ".join(a.get("text", "") if isinstance(a, dict) else str(a) for a in authors_data[:4])
                    elif isinstance(authors_data, dict):
                        authors = authors_data.get("text", "")
                    else:
                        authors = str(authors_data)

                    lines.append(f"\n- **{title}** ({year})")
                    lines.append(f"  Type: {pub_type} | Venue: {venue}")
                    lines.append(f"  Authors: {authors}")
                    if ee:
                        lines.append(f"  Electronic Edition: {ee}")
                    if url_link:
                        lines.append(f"  DBLP URL: {url_link}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing DBLP search: {e}"

