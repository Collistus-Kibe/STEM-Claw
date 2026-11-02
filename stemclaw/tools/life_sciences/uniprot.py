"""UniProtKB protein database search tool."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class UniProtInput(BaseModel):
    query: str = Field(..., description="Protein name, gene symbol, or UniProt ID (e.g. 'TP53' or 'insulin')")
    size: int = Field(default=5, ge=1, le=20, description="Max entries to return")


class UniProtSearchTool(BaseTool):
    name = "uniprot_search"
    description = (
        "Search UniProtKB for protein sequences, gene associations, organism taxonomies, and function annotations."
    )
    input_model = UniProtInput

    def run(self, query: str, size: int = 5) -> str:
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": query,
            "size": size,
            "format": "json",
            "fields": "accession,id,protein_name,gene_names,organism_name,length",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"UniProt API error {res.status_code}: {res.text}"
                data = res.json()
                results = data.get("results", [])
                if not results:
                    return f"No UniProt proteins found for '{query}'."

                lines = [f"UniProtKB Results for '{query}':"]
                for p in results:
                    acc = p.get("primaryAccession", "")
                    entry = p.get("uniProtkbId", "")
                    name_obj = p.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {})
                    protein_name = name_obj.get("value", "Unknown Protein")
                    organism = p.get("organism", {}).get("scientificName", "Unknown Organism")
                    genes = [
                        g.get("geneName", {}).get("value", "")
                        for g in p.get("genes", [])
                        if g.get("geneName")
                    ]
                    length = p.get("sequence", {}).get("length", 0)

                    lines.append(
                        f"• [{acc} / {entry}] {protein_name}\n"
                        f"  Organism: {organism} | Length: {length} aa\n"
                        f"  Genes: {', '.join(genes) if genes else 'N/A'}\n"
                        f"  URL: https://www.uniprot.org/uniprotkb/{acc}"
                    )
                return "\n\n".join(lines)
        except Exception as e:
            return f"Error querying UniProt API: {e}"

