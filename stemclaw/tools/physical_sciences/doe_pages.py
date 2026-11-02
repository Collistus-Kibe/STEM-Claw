"""DOE PAGES (Public Access Gateway for Energy & Science) search tool."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class DoePagesInput(BaseModel):
    query: str = Field(..., description="Energy, materials, or physical sciences query (e.g. 'lithium ion perovskite')")
    rows: int = Field(default=5, ge=1, le=20, description="Number of OSTI/DOE records to return")


class DoePagesSearchTool(BaseTool):
    name = "doe_pages_search"
    description = (
        "Search Department of Energy (DOE) PAGES records for materials science, condensed matter, and energy research."
    )
    input_model = DoePagesInput

    def run(self, query: str, rows: int = 5) -> str:
        url = "https://www.osti.gov/pages/api/v1/records"
        params = {"q": query, "rows": rows}
        headers = {"Accept": "application/json"}

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params, headers=headers)
                if res.status_code != 200:
                    return f"DOE PAGES error {res.status_code}: {res.text}"
                records = res.json()
                if not records:
                    return f"No DOE PAGES records found for '{query}'."

                lines = [f"DOE PAGES / OSTI Records for '{query}':"]
                for rec in records:
                    title = rec.get("title", "No Title")
                    authors = rec.get("authors", [])
                    author_names = [a.get("first_name", "") + " " + a.get("last_name", "") for a in authors]
                    osti_id = rec.get("osti_id", "")
                    doi = rec.get("doi", "")
                    date = rec.get("publication_date", "")

                    lines.append(
                        f"• {title}\n"
                        f"  Authors: {', '.join(author_names[:2])} | Date: {date}\n"
                        f"  OSTI ID: {osti_id} | DOI: {doi}"
                    )
                return "\n\n".join(lines)
        except Exception as e:
            return f"Error executing DOE PAGES search: {e}"

