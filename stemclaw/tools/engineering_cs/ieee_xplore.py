"""IEEE Xplore search tool for electrical engineering, robotics, and computing literature."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class IEEEXploreInput(BaseModel):
    query: str = Field(..., description="Topic keywords, IEEE transaction title, or author name")
    limit: int = Field(default=5, ge=1, le=20, description="Max articles to return")
    api_key: Optional[str] = Field(default=None, description="Optional IEEE Xplore API Key")


class IEEEXploreTool(BaseTool):
    name = "ieee_xplore"
    description = (
        "Search IEEE Xplore for IEEE transactions, conference proceedings, standards, "
        "and journals across robotics, electrical engineering, and computing."
    )
    input_model = IEEEXploreInput

    def run(self, query: str, limit: int = 5, api_key: Optional[str] = None) -> str:
        url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
        params = {
            "querytext": query,
            "max_records": limit,
        }
        if api_key:
            params["apikey"] = api_key
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code == 403 or (resp.status_code != 200 and not api_key):
                    # IEEE requires an API key for live search; return helpful guidance
                    return (
                        f"IEEE Xplore API query '{query}' requires an IEEE API key (IEEE_API_KEY).\n"
                        f"Status: {resp.status_code} {resp.reason_phrase}. "
                        f"Tip: Set IEEE_API_KEY in .stemclaw/.env to enable live IEEE Xplore queries, "
                        f"or use semantic_scholar_search / dblp_search for open indexing of IEEE publications."
                    )
                if resp.status_code != 200:
                    return f"IEEE Xplore API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                total = data.get("total_records", 0)
                articles = data.get("articles", [])

                if not articles:
                    return f"No IEEE Xplore articles found for query '{query}'."

                lines = [f"=== IEEE Xplore Results (Total: {total}, Showing: {len(articles)}) ==="]
                for art in articles:
                    title = art.get("title", "No Title")
                    year = art.get("publication_year", "N/A")
                    pub = art.get("publication_title", "IEEE Publication")
                    doi = art.get("doi", "")
                    citing = art.get("citing_paper_count", 0)
                    abstract = art.get("abstract") or "No abstract available."
                    if len(abstract) > 300:
                        abstract = abstract[:297] + "..."

                    authors = ", ".join(
                        a.get("full_name", "") for a in art.get("authors", {}).get("authors", []) if a.get("full_name")
                    )

                    lines.append(f"\n- **{title}** ({year}) [Citations: {citing}]")
                    lines.append(f"  Publication: {pub}")
                    if authors:
                        lines.append(f"  Authors: {authors}")
                    if doi:
                        lines.append(f"  DOI: https://doi.org/{doi}")
                    lines.append(f"  Abstract: {abstract}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing IEEE Xplore search: {e}"

