---
name: "cheminformatics-rdkit"
description: "Small molecule lookup, SMILES structure validation, Lipinski Rule of 5, Veber criteria, and physicochemical descriptors."
category: "physical_sciences"
allowed_tools:
  - pubchem_search
  - chembl_search
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 3
version: "2.0.0"
tags:
  - chemistry
  - cheminformatics
  - smiles
  - pubchem
  - molecular-descriptors
  - lipinski
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Cheminformatics & Molecular Descriptors Protocol

## 1. Overview & Cheminformatics Scope
This protocol governs the retrieval, structural validation, descriptor calculation, and drug-likeness assessment of chemical molecules. It ensures canonical representation via PubChem Compound ID (CID), SMILES, and InChIKey, and enforces quantitative Lipinski and Veber rule verification using deterministic Python calculations.

---

## 2. Decision Tree & Molecular Profiling Pipeline

```
User Query (Chemical Name / Formula / SMILES)
  │
  ├── 1. Compound Identification via PubChem
  │     └─► Invoke `pubchem_search(compound_name="<NAME>")`
  │           ├─► Hit: Extract CID, Canonical SMILES, Molecular Formula, Molecular Weight
  │           └─► Miss: Fall back to `chembl_search` with IUPAC or synonym
  │
  ├── 2. Structural Canonicalization
  │     ├─► Canonical SMILES: Unique string representation of molecular graph topology
  │     ├─► Isomeric SMILES: Encodes chiral centers (R/S) and geometric isomerism (E/Z)
  │     └─► InChIKey: 27-character hashed string for unambiguous database indexing
  │
  ├── 3. Drug-Likeness & Rule of Five Verification
  │     └─► Execute `python_eval` to test Lipinski criteria:
  │           1. Molecular Weight: $MW \le 500\text{ Da}$
  │           2. Lipophilicity: $\log P \le 5$ (octanol-water partition)
  │           3. Hydrogen Bond Donors: $HBD \le 5$ (sum of OH and NH groups)
  │           4. Hydrogen Bond Acceptors: $HBA \le 10$ (sum of O and N atoms)
  │     └─► Test Veber criteria:
  │           5. Rotatable Bonds: $N_{\text{rot}} \le 10$
  │           6. Topological Polar Surface Area: $\text{tPSA} \le 140\text{ \AA}^2$
  │
  ├── 4. Stoichiometry & Atom Counts
  │     └─► Parse molecular formula stoichiometry and check heavy atom count
  │
  └── 5. Literature & Bioactivity Cross-Reference
        └─► Check ChEMBL for clinical trials and pharmacology profiles
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Cause | Remediation Action | Example |
| :--- | :--- | :--- | :--- |
| **0 hits on common name** | Slang or non-indexed abbreviation | Lookup systematic IUPAC nomenclature or CAS registry number | `Tylenol` $\rightarrow$ `Acetaminophen` or `paracetamol` |
| **CID mismatch on stereoisomer** | Racemic vs single enantiomer query | Specify stereochemistry explicitly or request parent unchiral CID | `(R)-thalidomide` vs `thalidomide` |
| **Complex natural product fails** | Peptide or macromolecular entity | Query PubChem Substance or BioAssay database | `Vancomycin` $\rightarrow$ search parent aglycone CID |
| **Multi-component complex** | Metal coordinated or hydrate form | Strip hydrate and counter-ions to evaluate parent organic ligand | `Cisplatin` $\rightarrow$ query neutral square planar coordination |

---

## 4. Quantitative Cheminformatics Calculations (`python_eval`)

Never estimate molecular formulas, weights, or Lipinski compliance. Verify with deterministic Python evaluation:

### A. Lipinski Rule of 5 and Veber Scorecard
```python
def evaluate_drug_likeness(name: str, mw: float, logp: float, hbd: int, hba: int, rot_bonds: int, tpsa: float):
    violations = []
    if mw > 500.0:
        violations.append(f"MW > 500 Da ({mw:.1f})")
    if logp > 5.0:
        violations.append(f"LogP > 5.0 ({logp:.2f})")
    if hbd > 5:
        violations.append(f"HBD > 5 ({hbd})")
    if hba > 10:
        violations.append(f"HBA > 10 ({hba})")
    
    veber_violations = []
    if rot_bonds > 10:
        veber_violations.append(f"Rotatable Bonds > 10 ({rot_bonds})")
    if tpsa > 140.0:
        veber_violations.append(f"tPSA > 140 A^2 ({tpsa:.1f})")
        
    lipinski_pass = len(violations) <= 1  # 1 violation permitted under standard Ro5
    veber_pass = len(veber_violations) == 0
    
    print(f"=== {name} ===")
    print(f"Lipinski Ro5: {'PASS' if lipinski_pass else 'FAIL'} ({len(violations)} violations: {', '.join(violations) or 'None'})")
    print(f"Veber Filter: {'PASS' if veber_pass else 'FAIL'} ({', '.join(veber_violations) or 'Optimal'})")

# Example: Atorvastatin
evaluate_drug_likeness(
    name="Atorvastatin",
    mw=558.64,
    logp=4.46,
    hbd=4,
    hba=7,
    rot_bonds=12,
    tpsa=111.79
)
```

### B. Molecular Formula Molar Mass Verification
```python
import re

atomic_masses = {
    'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998,
    'P': 30.974, 'S': 32.06, 'Cl': 35.45, 'Br': 79.904, 'I': 126.90
}

def parse_formula_mass(formula: str) -> float:
    tokens = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    total_mass = 0.0
    for element, count_str in tokens:
        count = int(count_str) if count_str else 1
        total_mass += atomic_masses.get(element, 0.0) * count
    return total_mass

# Example: Caffeine C8H10N4O2
formula = "C8H10N4O2"
print(f"Calculated Molar Mass of {formula} = {parse_formula_mass(formula):.3f} g/mol")
```

---

## 5. Cheminformatics Output Schema

Present small molecules in this structured table:

| Compound Name | PubChem CID | Molecular Formula | Molecular Weight (g/mol) | Canonical SMILES | LogP | HBD / HBA | Ro5 Compliance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Aspirin | 2244 | C9H8O4 | 180.16 g/mol | `CC(=O)OC1=CC=CC=C1C(=O)O` | 1.19 | 1 / 4 | Pass (0 violations) |
| Imatinib | 5291 | C29H31N7O | 493.60 g/mol | `CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5` | 3.50 | 2 / 7 | Pass (0 violations) |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Invent SMILES Strings**: Never guess or construct SMILES strings from memory. Always fetch the verified string from `pubchem_search` or `chembl_search`.
2. **Explicit Valence Verification**: SMILES strings must represent chemically valid valences (e.g., carbon cannot have 5 bonds, aromatic rings must close properly).
3. **Always Report Canonical Over Arbitrary SMILES**: When comparing molecules, always use PubChem's Canonical SMILES representation to ensure 1-to-1 graph matching.
4. **Distinguish Neutral Molecule from Counter-Ions**: Clearly separate the active organic molecule from counter-ions like hydrochloride ($HCl$) or sodium ($Na^+$).
