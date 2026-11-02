---
name: "chemical-compound-screening"
description: "Screen bioactive compounds, clinical phase indications, target affinities, IC50/Ki conversions, and pharmacological mechanisms via ChEMBL."
category: "physical_sciences"
allowed_tools:
  - chembl_search
  - pubchem_search
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 4
version: "2.0.0"
tags:
  - chembl
  - pharmacology
  - drug-discovery
  - medicinal-chemistry
  - bioactivity
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Bioactive Compound Screening & Target Pharmacology Protocol

## 1. Overview & Chemical Pharmacology Scope
This protocol governs the identification, bioactivity profiling, target affinity assessment, and clinical development tracking of small molecules and chemical probes using the ChEMBL database and PubChem. It guarantees standard biochemical units, validates binding affinities ($K_i, K_d, \text{IC}_{50}, \text{EC}_{50}$), and computes logarithmic potency metrics ($\text{pIC}_{50}$).

---

## 2. Decision Tree & Screening Pipeline

```
User Query (Drug Name / Target Protein / ChEMBL ID)
  │
  ├── 1. Molecule Identification & ChEMBL Accession
  │     └─► Invoke `chembl_search(query="<NAME_OR_TARGET>", limit=5)`
  │           ├─► Hit: Extract ChEMBL ID (e.g. CHEMBL25 for Aspirin), pref_name, max_phase
  │           └─► Miss: Fall back to `pubchem_search` to find common synonyms/CID
  │
  ├── 2. Target Affinity & Bioactivity Metrics
  │     ├─► IC50: Concentration yielding 50% inhibition of target enzyme/receptor
  │     ├─► Ki: Equilibrium dissociation constant (Cheng-Prusoff corrected)
  │     ├─► Kd: Binding affinity determined via SPR or ITC
  │     └─► EC50: Half-maximal effective concentration in cellular phenotypic assays
  │
  ├── 3. Quantitative Potency Calculation
  │     └─► Execute `python_eval` to calculate:
  │           • $\text{pIC}_{50} = -\log_{10}(\text{IC}_{50} \times 10^{-9})$ (for nM values)
  │           • Cheng-Prusoff conversion: $K_i = \frac{\text{IC}_{50}}{1 + [S]/K_m}$
  │           • Selectivity Window: Ratio of off-target to on-target $\text{IC}_{50}$
  │
  ├── 4. Clinical Phase & Drug Likeness
  │     ├─► Phase 0 / Preclinical: Cell lines and animal models
  │     ├─► Phase 1 - 3: Active clinical trials (safety, dose escalation, pivotal efficacy)
  │     ├─► Phase 4: FDA / EMA approved and commercialized
  │     └─► Black Box / Withdrawn: Flag safety withdrawals or toxicities
  │
  └── 5. Structural Validation
        └─► Query `pubchem_search` for Canonical SMILES, 2D structure, and molecular weight
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Root Cause | Fallback Strategy | Example |
| :--- | :--- | :--- | :--- |
| **0 hits on brand name** | ChEMBL indexes by INN or chemical codes | Translate trade name to International Nonproprietary Name | `Lipitor` $\rightarrow$ `Atorvastatin` (`CHEMBL1487`) |
| **0 hits on developmental code** | Variant dash or spacing in code | Query without hyphenation or look up synonym via PubChem | `AZD-9291` $\rightarrow$ `AZD9291` OR `Osimertinib` (`CHEMBL3353410`) |
| **Target gene query fails** | ChEMBL distinguishes target name vs component | Query target organism and official UniProt symbol | `EGFR` $\rightarrow$ `Epidermal growth factor receptor` |
| **Ambiguous multi-component salt** | Salt forms yield duplicate entries | Select the parent free-base active moiety | `Imatinib mesylate` $\rightarrow$ `Imatinib` (`CHEMBL941`) |

---

## 4. Quantitative Bioactivity Calculations (`python_eval`)

Never fabricate or estimate $\text{pIC}_{50}$ or Cheng-Prusoff conversions. Execute exact calculations via `python_eval`:

### A. $\text{pIC}_{50}$ Potency Conversion
```python
import math

def calculate_pic50(ic50_nm: float) -> float:
    """Convert IC50 in nanomolar (nM) to logarithmic pIC50."""
    ic50_molar = ic50_nm * 1e-9
    return -math.log10(ic50_molar)

# Example: Nanomolar compound potency
ic50_values = {"Compound_A": 12.5, "Compound_B": 0.8, "Compound_C": 450.0}
for name, val in ic50_values.items():
    print(f"{name}: IC50 = {val} nM -> pIC50 = {calculate_pic50(val):.2f}")
```

### B. Cheng-Prusoff $K_i$ Derivation
```python
def cheng_prusoff(ic50_nm: float, substrate_conc_um: float, km_um: float) -> float:
    """Calculate absolute inhibition constant Ki from IC50 for competitive inhibitors."""
    return ic50_nm / (1.0 + (substrate_conc_um / km_um))

# Example: IC50 = 35 nM, [S] = 100 uM, Km = 25 uM
ki = cheng_prusoff(35.0, 100.0, 25.0)
print(f"Calculated Ki = {ki:.2f} nM (Selectivity Shift: {35.0 / ki:.1f}x)")
```

---

## 5. Pharmacology Evidence Matrix Output Schema

Summarize bioactive compounds using this standardized table:

| Molecule Name | ChEMBL Identifier | Max Clinical Phase | Target Protein | Affinity Parameter | Potency Value | $\text{pIC}_{50}$ | Mechanism of Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Imatinib | CHEMBL941 | Phase 4 (Approved) | BCR-ABL1 Tyrosine Kinase | $\text{IC}_{50}$ | 25 nM | 7.60 | Competitive ATP-binding site inhibitor |
| Osimertinib | CHEMBL3353410 | Phase 4 (Approved) | EGFR (T790M mutant) | $\text{IC}_{50}$ | 12 nM | 7.92 | Irreversible covalent kinase inhibitor |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Confuse $\text{IC}_{50}$ with $K_i$**: Always specify whether an affinity value represents assay-dependent $\text{IC}_{50}$ or thermodynamic equilibrium $K_i$.
2. **Clarify Assay Organism**: Always state whether bioactivity is measured against the human target or animal homolog (e.g. rat, mouse).
3. **Verify Salt vs Free Base**: Report molecular weight and stoichiometry based on the active uncharged free-base moiety unless specifically studying pharmacokinetic salt formulation.
4. **No Speculative Target Annotations**: Only report targets with experimental assay evidence logged in ChEMBL or confirmed literature; disallow hypothetical docking scores unless explicitly designated as *in silico*.
