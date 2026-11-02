"""Open Science Framework (OSF) Preprints search tool."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class OSFPreprintsInput(BaseModel):
    query: str = Field(..., description="Preprint title keywords, topic, or author across OSF partner preprint servers")
    limit: int = Field(default=5, ge=1, le=15, description="Max preprints to return")


class OSFPreprintsTool(BaseTool):
    name = "osf_preprints"
    description = (
        "Search Open Science Framework (OSF) Preprints across cross-disciplinary archives "
        "(OSF Preprints, PsyArXiv, SocArXiv, AgriXiv, MetaArXiv)."
    )
    input_model = OSFPreprintsInput

    def run(self, query: str, limit: int = 5) -> str:
        url = "https://api.osf.io/v2/preprints/"
        params = {
            "filter[title]": query,
            "page[size]": limit,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"OSF API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                items = data.get("data", [])

                if not items:
                    return f"No OSF preprints found matching title query '{query}'."

                lines = [f"=== OSF Preprints Results (Showing: {len(items)}) ==="]
                for item in items:
                    attrs = item.get("attributes", {})
                    title = attrs.get("title", "No Title")
                    date_pub = attrs.get("date_published", "N/A")[:10]
                    doi = attrs.get("doi", "")
                    description = attrs.get("description") or "No description provided."
                    if len(description) > 250:
                        description = description[:247] + "..."

                    links = item.get("links", {})
                    html_url = links.get("html", "")

                    lines.append(f"\n- **{title}** ({date_pub})")
                    if doi:
                        lines.append(f"  DOI: https://doi.org/{doi}")
                    if html_url:
                        lines.append(f"  OSF Link: {html_url}")
                    lines.append(f"  Description: {description}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing OSF Preprints search: {e}"

