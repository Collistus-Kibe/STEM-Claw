"""Unpaywall Open Access status and PDF resolver tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class UnpaywallLookupInput(BaseModel):
    doi: str = Field(..., description="Digital Object Identifier (DOI), e.g. '10.1038/nature12373'")
    email: Optional[str] = Field(default=None, description="Researcher email for polite API identification")


class UnpaywallLookupTool(BaseTool):
    name = "unpaywall_lookup"
    description = (
        "Check open access availability, legal PDF full-text links, and repository hosts "
        "for any scholarly paper using its DOI via Unpaywall."
    )
    input_model = UnpaywallLookupInput

    def run(self, doi: str, email: Optional[str] = None) -> str:
        clean_doi = doi.strip()
        if clean_doi.startswith("https://doi.org/"):
            clean_doi = clean_doi[16:]
        elif clean_doi.startswith("doi.org/"):
            clean_doi = clean_doi[8:]

        effective_email = email or "user@stemclaw.agent"
        url = f"https://api.unpaywall.org/v2/{clean_doi}"
        params = {"email": effective_email}
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code == 404:
                    return f"Unpaywall: DOI '{clean_doi}' was not found in the Unpaywall database."
                if resp.status_code != 200:
                    return f"Unpaywall API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                title = data.get("title", "Unknown Title")
                is_oa = data.get("is_oa", False)
                oa_status = data.get("oa_status", "closed")
                journal = data.get("journal_name", "Unknown Journal")
                year = data.get("year", "N/A")

                best_oa = data.get("best_oa_location") or {}
                pdf_url = best_oa.get("url_for_pdf") or best_oa.get("url") or ""
                license_type = best_oa.get("license") or "N/A"
                host_type = best_oa.get("host_type") or "publisher"

                lines = [
                    f"=== Unpaywall Open Access Record ===",
                    f"Title: {title} ({year})",
                    f"Journal: {journal}",
                    f"DOI: https://doi.org/{clean_doi}",
                    f"Is Open Access: {'YES (Free to read)' if is_oa else 'NO (Paywalled/Restricted)'}",
                    f"OA Status: {oa_status.upper()}",
                ]
                if is_oa and pdf_url:
                    lines.append(f"Direct Legal PDF / URL: {pdf_url}")
                    lines.append(f"Host Type: {host_type} | License: {license_type}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error querying Unpaywall: {e}"

