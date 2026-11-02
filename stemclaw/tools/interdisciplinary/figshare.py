"""Figshare research data and output search tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class FigshareSearchInput(BaseModel):
    query: str = Field(..., description="Research dataset, figure, poster, or presentation keyword")
    limit: int = Field(default=5, ge=1, le=15, description="Max Figshare items to return")


class FigshareSearchTool(BaseTool):
    name = "figshare_search"
    description = (
        "Search Figshare for open scientific datasets, experimental figures, posters, "
        "code, and supplemental materials."
    )
    input_model = FigshareSearchInput

    def run(self, query: str, limit: int = 5) -> str:
        url = "https://api.figshare.com/v2/articles/search"
        payload = {
            "search_for": query,
            "page_size": limit,
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "StemClaw-STEM-Research-Agent/1.0",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    return f"Figshare API returned status {resp.status_code}: {resp.text[:300]}"

                articles = resp.json()
                if not articles:
                    return f"No Figshare records found for query '{query}'."

                lines = [f"=== Figshare Open Research Outputs (Showing: {len(articles)}) ==="]
                for art in articles:
                    title = art.get("title", "No Title")
                    published = art.get("published_date", "N/A")[:10]
                    doi = art.get("doi", "")
                    fig_url = art.get("url_public_html", "")
                    timeline = art.get("timeline", {})

                    lines.append(f"\n- **{title}** ({published})")
                    if doi:
                        lines.append(f"  DOI: https://doi.org/{doi}")
                    if fig_url:
                        lines.append(f"  Figshare URL: {fig_url}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing Figshare search: {e}"

