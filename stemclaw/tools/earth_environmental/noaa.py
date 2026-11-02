"""NOAA Institutional Repository and Climate Data search tool."""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class NOAAClimateDataInput(BaseModel):
    query: str = Field(..., description="Climate topic, atmospheric keyword, oceanic study, or weather event")
    limit: int = Field(default=5, ge=1, le=15, description="Max climate records to return")
    token: Optional[str] = Field(default=None, description="Optional NOAA API token")


class NOAAClimateDataTool(BaseTool):
    name = "noaa_climate_data"
    description = (
        "Search the NOAA Climate Repository and Oceanographic/Atmospheric library "
        "for climate observations, marine assessments, weather models, and technical reports."
    )
    input_model = NOAAClimateDataInput

    def run(self, query: str, limit: int = 5, token: Optional[str] = None) -> str:
        # Query NOAA Institutional Repository OAI-PMH feed
        url = "https://repository.library.noaa.gov/fedora/oai"
        params = {
            "verb": "ListRecords",
            "metadataPrefix": "oai_dc",
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}
        if token:
            headers["token"] = token

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"NOAA Repository returned status {resp.status_code}: {resp.text[:300]}"

                xml_text = resp.text
                root = ET.fromstring(xml_text)

                ns = {
                    "oai": "http://www.openarchives.org/OAI/2.0/",
                    "dc": "http://purl.org/dc/elements/1.1/",
                    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
                }

                records = root.findall(".//oai:record", ns)
                matched_records = []
                query_lower = query.lower()

                for r in records:
                    metadata = r.find("oai:metadata/oai_dc:dc", ns)
                    if metadata is None:
                        continue

                    title_elem = metadata.find("dc:title", ns)
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"

                    desc_elem = metadata.find("dc:description", ns)
                    desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

                    subj_elems = metadata.findall("dc:subject", ns)
                    subjects = [s.text.strip() for s in subj_elems if s.text]

                    date_elem = metadata.find("dc:date", ns)
                    date = date_elem.text.strip() if date_elem is not None and date_elem.text else "N/A"

                    id_elems = metadata.findall("dc:identifier", ns)
                    links = [i.text.strip() for i in id_elems if i.text and i.text.startswith("http")]
                    link = links[0] if links else ""

                    # Filter by query if query is provided
                    content_blob = f"{title} {desc} {' '.join(subjects)}".lower()
                    if query_lower in content_blob or not query_lower:
                        matched_records.append({
                            "title": title,
                            "date": date,
                            "subjects": subjects,
                            "desc": desc,
                            "link": link,
                        })
                    if len(matched_records) >= limit:
                        break

                if not matched_records:
                    # If query didn't match first OAI batch, provide informative fallback search info
                    return (
                        f"NOAA OAI Repository checked. No direct matches found in current feed for '{query}'.\n"
                        f"Repository: https://repository.library.noaa.gov/ | Total Records Indexed: {len(records)}"
                    )

                lines = [f"=== NOAA Climate & Oceanographic Records (Showing {len(matched_records)}) ==="]
                for rec in matched_records:
                    lines.append(f"\n- **{rec['title']}** ({rec['date']})")
                    if rec["subjects"]:
                        lines.append(f"  Subjects: {', '.join(rec['subjects'][:4])}")
                    if rec["desc"]:
                        short_desc = rec["desc"][:240] + "..." if len(rec["desc"]) > 240 else rec["desc"]
                        lines.append(f"  Description: {short_desc}")
                    if rec["link"]:
                        lines.append(f"  Identifier URL: {rec['link']}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing NOAA search: {e}"

