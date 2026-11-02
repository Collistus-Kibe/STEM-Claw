"""NCBI Entrez E-utilities tools for biomedical literature and genomic search."""

import xml.etree.ElementTree as ET
from typing import Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool


class NCBIEsearchInput(BaseModel):
    term: str = Field(..., description="PubMed/Entrez search query (e.g. 'CRISPR Cas9 base editing')")
    db: str = Field(default="pubmed", description="NCBI database (pubmed, pmc, nuccore, protein)")
    retmax: int = Field(default=10, ge=1, le=50, description="Max PMIDs/IDs to return")


class NCBIEsearchTool(BaseTool):
    name = "ncbi_esearch"
    description = "Search NCBI databases (PubMed, PMC, GenBank) and return matching record IDs/PMIDs."
    input_model = NCBIEsearchInput

    def run(self, term: str, db: str = "pubmed", retmax: int = 10) -> str:
        settings = get_settings()
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": db,
            "term": term,
            "retmax": retmax,
            "retmode": "json",
        }
        if settings.ncbi_api_key:
            params["api_key"] = settings.ncbi_api_key

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"NCBI esearch error {res.status_code}: {res.text}"
                data = res.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                count = data.get("esearchresult", {}).get("count", "0")
                if not id_list:
                    return f"No results found on NCBI {db} for '{term}'."
                return (
                    f"NCBI {db} search: '{term}'\n"
                    f"Total matches: {count} | Top {len(id_list)} IDs: {', '.join(id_list)}"
                )
        except Exception as e:
            return f"Error executing NCBI esearch: {e}"


class NCBIEfetchInput(BaseModel):
    id: str = Field(..., description="Comma-separated PMIDs or accession numbers (e.g. '38123456,38123457')")
    db: str = Field(default="pubmed", description="Database: pubmed, pmc, protein, etc.")


class NCBIEfetchTool(BaseTool):
    name = "ncbi_efetch"
    description = "Fetch article abstracts, titles, and publication details from NCBI PubMed/Entrez by PMID."
    input_model = NCBIEfetchInput

    def run(self, id: str, db: str = "pubmed") -> str:
        settings = get_settings()
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": db,
            "id": id,
            "retmode": "xml",
        }
        if settings.ncbi_api_key:
            params["api_key"] = settings.ncbi_api_key

        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"NCBI efetch error {res.status_code}: {res.text}"

                # Parse XML response
                root = ET.fromstring(res.text)
                articles = []
                for article in root.findall(".//PubmedArticle"):
                    pmid_elem = article.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else "Unknown PMID"

                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No Title"

                    abstract_texts = [
                        a.text for a in article.findall(".//AbstractText") if a.text
                    ]
                    abstract = " ".join(abstract_texts) if abstract_texts else "No abstract provided."

                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else ""

                    articles.append(
                        f"• [PMID {pmid}] {title}\n"
                        f"  Journal: {journal}\n"
                        f"  Abstract: {abstract[:400]}..."
                    )

                if not articles:
                    return f"Raw fetch result for ID {id}:\n{res.text[:600]}"
                return "\n\n".join(articles)
        except Exception as e:
            return f"Error executing NCBI efetch: {e}"

