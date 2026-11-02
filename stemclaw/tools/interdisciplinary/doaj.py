"""DOAJ Directory of Open Access Journals search tool."""

from typing import Any, Dict, List, Optional
import urllib.parse
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class DOAJSearchInput(BaseModel):
    query: str = Field(..., description="Open access journal article title, keywords, or author")
    limit: int = Field(default=5, ge=1, le=15, description="Max peer-reviewed open access articles to return")


class DOAJSearchTool(BaseTool):
    name = "doaj_search"
    description = (
        "Search the Directory of Open Access Journals (DOAJ) for high-quality, peer-reviewed, "
        "fully open access scientific articles across all research disciplines."
    )
    input_model = DOAJSearchInput

    def run(self, query: str, limit: int = 5) -> str:
        encoded_query = urllib.parse.quote(query)
        url = f"https://doaj.org/api/search/articles/{encoded_query}"
        params = {"pageSize": limit}
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"DOAJ API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                total = data.get("total", 0)
                results = data.get("results", [])

                if not results:
                    return f"No DOAJ open access articles found for query '{query}'."

                lines = [f"=== DOAJ Open Access Articles (Total: {total:,}, Showing: {len(results)}) ==="]
                for item in results:
                    bibjson = item.get("bibjson", {})
                    title = bibjson.get("title", "No Title")
                    year = bibjson.get("year", "N/A")
                    journal_info = bibjson.get("journal", {})
                    journal_title = journal_info.get("title", "Open Access Journal")
                    abstract = bibjson.get("abstract") or "No abstract provided."
                    if len(abstract) > 250:
                        abstract = abstract[:247] + "..."

                    authors_list = [a.get("name", "") for a in bibjson.get("author", []) if a.get("name")]
                    authors_str = ", ".join(authors_list[:3])

                    links = bibjson.get("link", [])
                    fulltext_url = ""
                    for link_obj in links:
                        if link_obj.get("type") == "fulltext":
                            fulltext_url = link_obj.get("url", "")
                            break
                    if not fulltext_url and links:
                        fulltext_url = links[0].get("url", "")

                    lines.append(f"\n- **{title}** ({year})")
                    lines.append(f"  Journal: {journal_title}")
                    if authors_str:
                        lines.append(f"  Authors: {authors_str}")
                    if fulltext_url:
                        lines.append(f"  Full Text Link: {fulltext_url}")
                    lines.append(f"  Abstract: {abstract}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing DOAJ search: {e}"

