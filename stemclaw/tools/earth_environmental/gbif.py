"""GBIF Global Biodiversity Information Facility occurrence and species tools."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class GBIFOccurrencesInput(BaseModel):
    query: str = Field(..., description="Scientific or vernacular species name, taxon, or geographic region")
    country: Optional[str] = Field(default=None, description="2-letter ISO country code (e.g. 'US', 'BR', 'KE')")
    limit: int = Field(default=5, ge=1, le=20, description="Max occurrence records to return")


class GBIFOccurrencesTool(BaseTool):
    name = "gbif_occurrences"
    description = (
        "Search GBIF occurrence records for geospatial biodiversity observations, museum specimens, "
        "coordinates (lat/lon), basis of record, and observation dates."
    )
    input_model = GBIFOccurrencesInput

    def run(self, query: str, country: Optional[str] = None, limit: int = 5) -> str:
        url = "https://api.gbif.org/v1/occurrence/search"
        params: Dict[str, Any] = {
            "q": query,
            "limit": limit,
        }
        if country:
            params["country"] = country.upper()

        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"GBIF Occurrence API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                count = data.get("count", 0)
                results = data.get("results", [])

                if not results:
                    return f"No GBIF occurrences found for query '{query}'."

                lines = [f"=== GBIF Occurrence Records (Total Occurrences: {count:,}, Showing: {len(results)}) ==="]
                for rec in results:
                    scientific_name = rec.get("scientificName", "Unknown Taxon")
                    vernacular = rec.get("vernacularName", "")
                    country_name = rec.get("country", "Unknown Country")
                    decimal_lat = rec.get("decimalLatitude")
                    decimal_lon = rec.get("decimalLongitude")
                    coords = f"({decimal_lat}, {decimal_lon})" if decimal_lat and decimal_lon else "No coordinates"
                    event_date = rec.get("eventDate") or rec.get("year") or "N/A"
                    basis = rec.get("basisOfRecord", "OBSERVATION")
                    dataset_key = rec.get("datasetKey", "")

                    lines.append(f"\n- **{scientific_name}**" + (f" ({vernacular})" if vernacular else ""))
                    lines.append(f"  Location: {country_name} | Coords: {coords}")
                    lines.append(f"  Date: {event_date} | Basis: {basis}")
                    if dataset_key:
                        lines.append(f"  Dataset Key: {dataset_key}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing GBIF occurrence search: {e}"


class GBIFSpeciesInput(BaseModel):
    query: str = Field(..., description="Species scientific name or vernacular name to look up taxonomic hierarchy")
    limit: int = Field(default=5, ge=1, le=15, description="Max species taxa to return")


class GBIFSpeciesTool(BaseTool):
    name = "gbif_species"
    description = (
        "Look up species taxonomy in GBIF backbone taxonomy (kingdom, phylum, class, order, "
        "family, genus, species, taxonomic status)."
    )
    input_model = GBIFSpeciesInput

    def run(self, query: str, limit: int = 5) -> str:
        url = "https://api.gbif.org/v1/species/search"
        params = {
            "q": query,
            "limit": limit,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"GBIF Species API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                results = data.get("results", [])

                if not results:
                    return f"No GBIF species found for '{query}'."

                lines = [f"=== GBIF Species Backbone Taxonomy (Showing: {len(results)}) ==="]
                for sp in results:
                    canonical = sp.get("canonicalName") or sp.get("scientificName", "Unknown")
                    rank = sp.get("rank", "SPECIES")
                    status = sp.get("status", "ACCEPTED")
                    kingdom = sp.get("kingdom", "N/A")
                    phylum = sp.get("phylum", "N/A")
                    order = sp.get("order", "N/A")
                    family = sp.get("family", "N/A")
                    genus = sp.get("genus", "N/A")
                    taxon_id = sp.get("key", "")

                    lines.append(f"\n- **{canonical}** [{rank} - {status}] (GBIF ID: {taxon_id})")
                    lines.append(f"  Hierarchy: {kingdom} > {phylum} > {order} > {family} > {genus}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing GBIF species search: {e}"

