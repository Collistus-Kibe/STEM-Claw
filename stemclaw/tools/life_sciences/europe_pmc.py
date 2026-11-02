"""Europe PMC REST tool for European biological and medical literature."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class EuropePMCInput(BaseModel):
    query: str = Field(..., description="Europe PMC search query (e.g. 'BRAF V600E melanoma')")
    page_size: int = Field(default=5, ge=1, le=25, description="Number of results to return")


class EuropePMCSearchTool(BaseTool):
    name = "europe_pmc_search"
    description = (
        "Search Europe PMC open-access papers, preprints, patents, and biological records."
    )
    input_model = EuropePMCInput

    def run(self, query: str, page_size: int = 5) -> str:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": query,
            "format": "json",
            "pageSize": page_size,
            "resultType": "core",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"Europe PMC error {res.status_code}: {res.text}"
                data = res.json()
                results = data.get("resultList", {}).get("result", [])
                total = data.get("hitCount", 0)
                if not results:
                    return f"No Europe PMC results found for '{query}'."

                items = [f"Europe PMC Search: '{query}' (Found {total} records)"]
                for r in results:
                    title = r.get("title", "No Title")
                    author = r.get("authorString", "Unknown authors")
                    doi = r.get("doi", "No DOI")
                    pmid = r.get("pmid", "No PMID")
                    journal = r.get("journalTitle", "")
                    isOpen = "Open Access" if r.get("isOpenAccess") == "Y" else "Subscription"
                    items.append(
                        f"• {title}\n"
                        f"  Authors: {author[:80]}...\n"
                        f"  DOI: {doi} | PMID: {pmid} | [{isOpen}] {journal}"
                    )
                return "\n\n".join(items)
        except Exception as e:
            return f"Error querying Europe PMC: {e}"

