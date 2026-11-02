"""ORCID researcher and scholarly record lookup tool."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class OrcidInput(BaseModel):
    query: str = Field(..., description="Researcher name or 16-digit ORCID ID (e.g. '0000-0002-1825-0097' or 'Jennifer Doudna')")


class OrcidLookupTool(BaseTool):
    name = "orcid_lookup"
    description = (
        "Look up researcher scholarly profiles, publication records, and institutional affiliations via ORCID."
    )
    input_model = OrcidInput

    def run(self, query: str) -> str:
        cleaned = query.strip()
        headers = {"Accept": "application/json"}

        # If it looks like a direct ORCID ID
        if len(cleaned) == 19 and cleaned.count("-") == 3:
            url = f"https://pub.orcid.org/v3.0/{cleaned}/person"
            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.get(url, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        name_obj = data.get("name", {})
                        given = name_obj.get("given-names", {}).get("value", "")
                        family = name_obj.get("family-name", {}).get("value", "")
                        return f"ORCID Profile: {given} {family} (https://orcid.org/{cleaned})"
            except Exception:
                pass

        # Otherwise search by name query
        search_url = "https://pub.orcid.org/v3.0/search"
        params = {"q": cleaned, "rows": 5}
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(search_url, params=params, headers=headers)
                if res.status_code != 200:
                    return f"ORCID search error {res.status_code}: {res.text}"
                data = res.json()
                results = data.get("result", [])
                if not results:
                    return f"No ORCID profiles found for '{cleaned}'."

                lines = [f"ORCID Search Results for '{cleaned}':"]
                for r in results:
                    orcid = r.get("orcid-identifier", {}).get("path", "")
                    uri = r.get("orcid-identifier", {}).get("uri", "")
                    lines.append(f"• ORCID ID: {orcid} ({uri})")
                return "\n".join(lines)
        except Exception as e:
            return f"Error querying ORCID API: {e}"

