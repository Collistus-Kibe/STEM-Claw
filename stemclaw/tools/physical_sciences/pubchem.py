"""PubChem PUG REST tool for chemical properties and molecular structures."""

import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class PubchemInput(BaseModel):
    compound_name: str = Field(..., description="Chemical compound name or formula (e.g. 'caffeine', 'paracetamol', 'C6H12O6')")


class PubchemSearchTool(BaseTool):
    name = "pubchem_search"
    description = (
        "Retrieve chemical properties, molecular formula, molecular weight, and SMILES from PubChem PUG REST."
    )
    input_model = PubchemInput

    def run(self, compound_name: str) -> str:
        clean_name = compound_name.strip()
        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
            f"{clean_name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
        )

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url)
                if res.status_code == 404:
                    return f"PubChem compound '{compound_name}' not found."
                if res.status_code != 200:
                    return f"PubChem API error {res.status_code}: {res.text}"

                data = res.json()
                properties = data.get("PropertyTable", {}).get("Properties", [])
                if not properties:
                    return f"No chemical properties found on PubChem for '{compound_name}'."

                p = properties[0]
                cid = p.get("CID", "")
                formula = p.get("MolecularFormula", "")
                weight = p.get("MolecularWeight", "")
                iupac = p.get("IUPACName", "")
                smiles = p.get("CanonicalSMILES", "")

                return (
                    f"PubChem Compound: {compound_name.title()} (CID {cid})\n"
                    f"• Molecular Formula: {formula}\n"
                    f"• Molecular Weight: {weight} g/mol\n"
                    f"• IUPAC Name: {iupac}\n"
                    f"• Canonical SMILES: {smiles}\n"
                    f"• PubChem URL: https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                )
        except Exception as e:
            return f"Error executing PubChem lookup: {e}"

