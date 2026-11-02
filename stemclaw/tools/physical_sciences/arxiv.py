"""arXiv query tool for physics, mathematics, and quantitative science."""

import xml.etree.ElementTree as ET
from typing import Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class ArxivInput(BaseModel):
    query: str = Field(..., description="Scientific topic, equation, or paper title to search on arXiv")
    max_results: int = Field(default=5, ge=1, le=25, description="Max papers to return")
    category: Optional[str] = Field(
        default=None,
        description="Optional arXiv subject filter (e.g. 'quant-ph', 'cond-mat', 'hep-th', 'astro-ph')",
    )


class ArxivSearchTool(BaseTool):
    name = "arxiv_search"
    description = (
        "Search arXiv preprints for quantum physics, condensed matter, high energy physics, astrophysics, and math."
    )
    input_model = ArxivInput

    def run(self, query: str, max_results: int = 5, category: Optional[str] = None) -> str:
        search_term = query
        if category:
            search_term = f"cat:{category} AND all:{query}"
        else:
            search_term = f"all:{query}"

        url = "https://export.arxiv.org/api/query"
        params = {
            "search_query": search_term,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"arXiv API error {res.status_code}: {res.text}"

                # Parse Atom XML
                root = ET.fromstring(res.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", ns)
                if not entries:
                    return f"No arXiv papers found matching '{query}'."

                items = [f"arXiv Search Results for '{query}':"]
                for e in entries:
                    title_elem = e.find("atom:title", ns)
                    title = " ".join(title_elem.text.split()) if title_elem is not None and title_elem.text else "Untitled"

                    summary_elem = e.find("atom:summary", ns)
                    summary = " ".join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else ""

                    id_elem = e.find("atom:id", ns)
                    arxiv_url = id_elem.text if id_elem is not None and id_elem.text else ""

                    published_elem = e.find("atom:published", ns)
                    published = published_elem.text[:10] if published_elem is not None and published_elem.text else ""

                    authors = [
                        a.find("atom:name", ns).text
                        for a in e.findall("atom:author", ns)
                        if a.find("atom:name", ns) is not None
                    ]
                    author_str = ", ".join(authors[:3]) + (f" + {len(authors)-3} more" if len(authors) > 3 else "")

                    items.append(
                        f"• {title}\n"
                        f"  Authors: {author_str} | Published: {published}\n"
                        f"  arXiv: {arxiv_url}\n"
                        f"  Summary: {summary[:280]}..."
                    )
                return "\n\n".join(items)
        except Exception as e:
            return f"Error executing arXiv search: {e}"

