"""bioRxiv API tool for biological preprints."""

from datetime import datetime, timedelta, timezone
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class BioRxivInput(BaseModel):
    query: str = Field(..., description="Topic keywords to search in bioRxiv preprints")
    days_back: int = Field(default=30, ge=1, le=180, description="How many days back to search")
    max_results: int = Field(default=5, ge=1, le=20, description="Max preprints to return")


class BioRxivSearchTool(BaseTool):
    name = "biorxiv_search"
    description = (
        "Search recent biological and biomedical preprints deposited on bioRxiv."
    )
    input_model = BioRxivInput

    def run(self, query: str, days_back: int = 30, max_results: int = 5) -> str:
        end_d = datetime.now(timezone.utc)
        start_d = end_d - timedelta(days=days_back)
        interval = f"{start_d.strftime('%Y-%m-%d')}/{end_d.strftime('%Y-%m-%d')}"
        url = f"https://api.biorxiv.org/details/biorxiv/{interval}/0/json"

        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.get(url)
                if res.status_code != 200:
                    return f"bioRxiv API error {res.status_code}: {res.text}"
                data = res.json()
                collection = data.get("collection", [])
                if not collection:
                    return f"No bioRxiv preprints retrieved for window {interval}."

                kw = query.lower().strip()
                matches = []
                for p in collection:
                    title = p.get("title", "")
                    abstract = p.get("abstract", "")
                    if kw in title.lower() or kw in abstract.lower():
                        matches.append(p)
                    if len(matches) >= max_results:
                        break

                if not matches:
                    # Fallback: return top recent if no keyword match
                    matches = collection[:max_results]

                lines = [f"bioRxiv Preprints (Window {interval}) query: '{query}':"]
                for m in matches:
                    title = m.get("title", "No Title")
                    authors = m.get("authors", "")
                    doi = m.get("doi", "")
                    date = m.get("date", "")
                    category = m.get("category", "")
                    lines.append(
                        f"• {title}\n"
                        f"  Authors: {authors[:70]}... | Date: {date} | Category: {category}\n"
                        f"  DOI: https://doi.org/{doi}"
                    )
                return "\n\n".join(lines)
        except Exception as e:
            return f"Error querying bioRxiv API: {e}"

