"""ChEMBL database tool for bioactive molecules and pharmacology."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class ChemblInput(BaseModel):
    query: str = Field(..., description="Molecule name, drug, or ChEMBL ID (e.g. 'aspirin', 'CHEMBL25', 'imatinib')")
    limit: int = Field(default=5, ge=1, le=20, description="Max molecules to return")


class ChemblSearchTool(BaseTool):
    name = "chembl_search"
    description = (
        "Search ChEMBL database for bioactive molecules, drug indications, chemical structures, and SMILES."
    )
    input_model = ChemblInput

    def run(self, query: str, limit: int = 5) -> str:
        cleaned = query.strip()
        url = "https://www.ebi.ac.uk/chembl/api/data/molecule"

        # Check if direct ChEMBL ID
        if cleaned.upper().startswith("CHEMBL"):
            params = {"molecule_chembl_id": cleaned.upper(), "format": "json"}
        else:
            params = {"pref_name__icontains": cleaned, "limit": limit, "format": "json"}

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return f"ChEMBL error {res.status_code}: {res.text}"
                data = res.json()
                molecules = data.get("molecules", [])
                if not molecules:
                    return f"No ChEMBL molecules found for '{query}'."

                lines = [f"ChEMBL Molecules for '{query}':"]
                for m in molecules:
                    chembl_id = m.get("molecule_chembl_id", "")
                    pref_name = m.get("pref_name") or "Unspecified Name"
                    structs = m.get("molecule_structures") or {}
                    smiles = structs.get("canonical_smiles", "No SMILES")
                    mol_type = m.get("molecule_type", "")
                    max_phase = m.get("max_phase", "0")

                    lines.append(
                        f"• [{chembl_id}] {pref_name} ({mol_type})\n"
                        f"  Max Clinical Phase: {max_phase}\n"
                        f"  Canonical SMILES: {smiles}\n"
                        f"  URL: https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id}/"
                    )
                return "\n\n".join(lines)
        except Exception as e:
            return f"Error executing ChEMBL search: {e}"

