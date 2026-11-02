"""Semantic Scholar Graph API search and citation/reference tools."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class SemanticScholarSearchInput(BaseModel):
    query: str = Field(..., description="Academic search query, computer science topic, or paper title")
    limit: int = Field(default=5, ge=1, le=20, description="Max papers to return")
    api_key: Optional[str] = Field(default=None, description="Optional Semantic Scholar API key for higher rate limits")


class SemanticScholarSearchTool(BaseTool):
    name = "semantic_scholar_search"
    description = (
        "Search Semantic Scholar's academic graph for computer science papers, citations, "
        "abstracts, author profiles, and external IDs (ArXiv, DOI)."
    )
    input_model = SemanticScholarSearchInput

    def run(self, query: str, limit: int = 5, api_key: Optional[str] = None) -> str:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        fields = "paperId,title,authors,year,abstract,citationCount,url,externalIds"
        params = {
            "query": query,
            "limit": limit,
            "fields": fields,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}
        if api_key:
            headers["x-api-key"] = api_key

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"Semantic Scholar API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                total = data.get("total", 0)
                papers = data.get("data", [])

                if not papers:
                    return f"No Semantic Scholar papers found for query '{query}'."

                lines = [f"=== Semantic Scholar Search (Total: {total}, Showing: {len(papers)}) ==="]
                for p in papers:
                    paper_id = p.get("paperId", "")
                    title = p.get("title", "No Title")
                    year = p.get("year", "N/A")
                    citations = p.get("citationCount", 0)
                    abstract = p.get("abstract") or "No abstract available."
                    if len(abstract) > 300:
                        abstract = abstract[:297] + "..."

                    authors_list = [a.get("name", "") for a in p.get("authors", []) if a.get("name")]
                    authors_str = ", ".join(authors_list[:4])

                    url_link = p.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}"

                    lines.append(f"\n- **{title}** ({year}) [Citations: {citations}]")
                    lines.append(f"  Paper ID: {paper_id}")
                    lines.append(f"  Authors: {authors_str}")
                    lines.append(f"  URL: {url_link}")
                    lines.append(f"  Abstract: {abstract}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing Semantic Scholar search: {e}"


class SemanticScholarRefsInput(BaseModel):
    paper_id: str = Field(..., description="Semantic Scholar Paper ID, DOI, or arXiv ID (e.g. 'arXiv:1706.03762')")
    mode: str = Field(default="references", description="'references' (papers it cites) or 'citations' (papers citing it)")
    limit: int = Field(default=8, ge=1, le=30, description="Max citation/reference entries to return")
    api_key: Optional[str] = Field(default=None, description="Optional Semantic Scholar API key")


class SemanticScholarRefsTool(BaseTool):
    name = "semantic_scholar_refs"
    description = (
        "Inspect citation trees and references for a given paper via Semantic Scholar graph. "
        "Allows navigating forward (citations) or backward (references) in computer science research."
    )
    input_model = SemanticScholarRefsInput

    def run(self, paper_id: str, mode: str = "references", limit: int = 8, api_key: Optional[str] = None) -> str:
        clean_mode = "citations" if mode.lower() == "citations" else "references"
        fields = "paperId,title,authors,year,citationCount,url"
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/{clean_mode}"
        params = {
            "limit": limit,
            "fields": fields,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}
        if api_key:
            headers["x-api-key"] = api_key

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"Semantic Scholar Graph API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                items = data.get("data", [])

                if not items:
                    return f"No {clean_mode} found for paper '{paper_id}'."

                lines = [f"=== Semantic Scholar {clean_mode.capitalize()} for Paper '{paper_id}' (Showing {len(items)}) ==="]
                for item in items:
                    target_paper = item.get("citedPaper") or item.get("citingPaper") or item
                    pid = target_paper.get("paperId", "")
                    title = target_paper.get("title", "No Title")
                    year = target_paper.get("year", "N/A")
                    citations = target_paper.get("citationCount", 0)
                    authors_list = [a.get("name", "") for a in target_paper.get("authors", []) if a.get("name")]
                    authors_str = ", ".join(authors_list[:3])
                    link = target_paper.get("url") or (f"https://www.semanticscholar.org/paper/{pid}" if pid else "")

                    lines.append(f"\n- **{title}** ({year}) [Citations: {citations}]")
                    if authors_str:
                        lines.append(f"  Authors: {authors_str}")
                    if link:
                        lines.append(f"  Link: {link}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error fetching Semantic Scholar {clean_mode}: {e}"

