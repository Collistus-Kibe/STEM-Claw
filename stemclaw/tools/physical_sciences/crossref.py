"""Crossref DOI and scholarly publication search tool."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool


class CrossrefInput(BaseModel):
    query: str = Field(..., description="Query terms or publication title to search on Crossref")
    rows: int = Field(default=5, ge=1, le=20, description="Max results to return")


class CrossrefSearchTool(BaseTool):
    name = "crossref_search"
    description = (
        "Query Crossref metadata registry for official peer-reviewed publisher records and DOIs."
    )
    input_model = CrossrefInput

    def run(self, query: str, rows: int = 5) -> str:
        settings = get_settings()
        url = "https://api.crossref.org/works"
        params = {"query": query, "rows": rows}
        headers = {}
        if settings.crossref_mailto:
            headers["User-Agent"] = f"StemClaw/0.1.0 (mailto:{settings.crossref_mailto})"

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params, headers=headers)
                if res.status_code != 200:
                    return f"Crossref error {res.status_code}: {res.text}"
                data = res.json()
                items = data.get("message", {}).get("items", [])
                if not items:
                    return f"No Crossref records found for '{query}'."

                lines = [f"Crossref Results for '{query}':"]
                for it in items:
                    titles = it.get("title", [])
                    title = titles[0] if titles else "No Title"
                    doi = it.get("DOI", "")
                    publisher = it.get("publisher", "")
                    container = it.get("container-title", [])
                    journal = container[0] if container else publisher

                    lines.append(
                        f"• {title}\n"
                        f"  Publisher/Journal: {journal}\n"
                        f"  DOI: https://doi.org/{doi}"
                    )
                return "\n\n".join(lines)
        except Exception as e:
            return f"Error executing Crossref search: {e}"

