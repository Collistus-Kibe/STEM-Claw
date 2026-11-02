"""CORE global aggregator of open access research papers search tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class CORESearchInput(BaseModel):
    query: str = Field(..., description="Cross-disciplinary research topic, title keywords, or author")
    limit: int = Field(default=5, ge=1, le=15, description="Max papers to return")
    api_key: Optional[str] = Field(default=None, description="Optional CORE API key (CORE_API_KEY)")


class CORESearchTool(BaseTool):
    name = "core_search"
    description = (
        "Search CORE (core.ac.uk), the world's largest aggregator of open access research papers "
        "harvested from institutional repositories and journals."
    )
    input_model = CORESearchInput

    def run(self, query: str, limit: int = 5, api_key: Optional[str] = None) -> str:
        url = "https://api.core.ac.uk/v3/search/works"
        params = {
            "q": query,
            "limit": limit,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code == 401 and not api_key:
                    return (
                        f"CORE API requires an API key for search endpoints (status 401).\n"
                        f"Tip: Set CORE_API_KEY in .stemclaw/.env to enable direct CORE searches, "
                        f"or use doaj_search, zenodo_search, and unpaywall_lookup for open access research."
                    )
                if resp.status_code != 200:
                    return f"CORE API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                total = data.get("totalHits", 0)
                results = data.get("results", [])

                if not results:
                    return f"No CORE publications found for query '{query}'."

                lines = [f"=== CORE Open Access Search (Total Hits: {total:,}, Showing: {len(results)}) ==="]
                for r in results:
                    title = r.get("title", "No Title")
                    year = r.get("yearPublished", "N/A")
                    abstract = r.get("abstract") or "No abstract provided."
                    if len(abstract) > 250:
                        abstract = abstract[:247] + "..."

                    authors_list = [a.get("name", "") for a in r.get("authors", []) if a.get("name")]
                    authors_str = ", ".join(authors_list[:3])
                    doi = r.get("doi", "")
                    download_url = r.get("downloadUrl", "")

                    lines.append(f"\n- **{title}** ({year})")
                    if authors_str:
                        lines.append(f"  Authors: {authors_str}")
                    if doi:
                        lines.append(f"  DOI: https://doi.org/{doi}")
                    if download_url:
                        lines.append(f"  Full Text: {download_url}")
                    lines.append(f"  Abstract: {abstract}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing CORE search: {e}"

