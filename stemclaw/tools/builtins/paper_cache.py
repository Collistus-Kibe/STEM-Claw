"""Local paper cache search built-in tool."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from stemclaw.cache.db import get_paper_cache
from stemclaw.tools.base import BaseTool


class SearchLocalPapersInput(BaseModel):
    query: str = Field(..., description="Keywords, author name, title fragment, or DOI to search in offline local paper cache")
    limit: int = Field(default=5, ge=1, le=20, description="Max cached papers to return")


class SearchLocalPapersTool(BaseTool):
    name = "search_local_papers"
    description = (
        "Search the offline local research cache (.stemclaw/cache.db) for scientific papers, "
        "abstracts, and metadata retrieved in previous turns or sessions. "
        "Instant and does not consume API rate limits."
    )
    input_model = SearchLocalPapersInput

    def run(self, query: str, limit: int = 5) -> str:
        db = get_paper_cache()
        results = db.search_papers(query, limit=limit)
        total = db.count()

        if not results:
            return (
                f"No papers matching '{query}' found in local cache.\n"
                f"Total papers currently stored in local cache: {total}. "
                f"Try using external literature tools (ncbi_esearch, arxiv_search, semantic_scholar_search, etc.) "
                f"which automatically populate the local cache."
            )

        lines = [f"=== Local Paper Cache Search (Found {len(results)} matches, Total in Cache: {total}) ==="]
        for p in results:
            title = p.get("title", "No Title")
            year = p.get("year") or "N/A"
            authors = p.get("authors") or "Unknown Authors"
            venue = p.get("venue") or ""
            doi = p.get("doi") or ""
            source = p.get("source") or "local"
            abstract = p.get("abstract") or "No abstract stored."
            if len(abstract) > 250:
                abstract = abstract[:247] + "..."

            lines.append(f"\n- **{title}** ({year}) [Source: {source}]")
            if venue:
                lines.append(f"  Venue: {venue}")
            lines.append(f"  Authors: {authors}")
            if doi:
                lines.append(f"  DOI: https://doi.org/{doi}")
            lines.append(f"  Abstract: {abstract}")

        return "\n".join(lines)

