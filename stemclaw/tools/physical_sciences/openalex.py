"""OpenAlex open scientific graph search tool."""

from typing import Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool


class OpenAlexInput(BaseModel):
    search: str = Field(..., description="Topic, author, or research title to search on OpenAlex")
    per_page: int = Field(default=5, ge=1, le=25, description="Number of results to return")


class OpenAlexSearchTool(BaseTool):
    name = "openalex_search"
    description = (
        "Search OpenAlex for open-access papers across physical sciences, materials, chemistry, and citations."
    )
    input_model = OpenAlexInput

    def run(self, search: str, per_page: int = 5) -> str:
        settings = get_settings()
        url = "https://api.openalex.org/works"
        params = {
            "search": search,
            "per_page": per_page,
        }
        if settings.openalex_mailto:
            params["mailto"] = settings.openalex_mailto

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"OpenAlex error {res.status_code}: {res.text}"
                data = res.json()
                results = data.get("results", [])
                total = data.get("meta", {}).get("count", 0)
                if not results:
                    return f"No OpenAlex papers found matching '{search}'."

                lines = [f"OpenAlex Scholarly Graph: '{search}' (Total matches: {total}):"]
                for w in results:
                    title = w.get("title", "No Title")
                    doi = w.get("doi", "N/A")
                    pub_year = w.get("publication_year", "N/A")
                    cited_count = w.get("cited_by_count", 0)
                    oa_url = w.get("open_access", {}).get("oa_url") or doi

                    lines.append(
                        f"• {title}\n"
                        f"  Year: {pub_year} | Citations: {cited_count} | DOI: {doi}\n"
                        f"  Open Access URL: {oa_url}"
                    )
                return "\n\n".join(lines)
        except Exception as e:
            return f"Error executing OpenAlex query: {e}"

