---
name: "protein-sequence-analysis"
description: "Retrieve UniProt sequences, evaluate structural domains, compute biochemical constants, and cross-reference proteomic annotations."
category: "life_sciences"
allowed_tools:
  - uniprot_search
  - europe_pmc_search
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 2
version: "2.0.0"
tags:
  - proteomics
  - uniprot
  - sequences
  - protein-structure
  - bioinformatics
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Protein Sequence & Structural Analysis Protocol

## 1. Overview & Proteomic Scope
This protocol governs the retrieval, sequence inspection, physicochemical characterization, and structural cross-referencing of proteins. It maps vernacular gene symbols to canonical UniProtKB accession codes, verifies catalytic/binding residues, calculates exact physical parameters, and bridges sequence data with experimental structure databases (PDB, AlphaFold).

---

## 2. Decision Tree & Proteomic Workflow

```
User Query (Gene Symbol / Protein / Accession)
  │
  ├── 1. Identifier Resolution & Accession Lookup
  │     └─► Invoke `uniprot_search(query="gene:<SYMBOL> AND organism_id:9606", size=5)`
  │           ├─► Hit: Extract canonical Accession (e.g., P04637 for human TP53), entry name, length
  │           └─► Ambiguous/Miss: Expand search query without organism constraint
  │
  ├── 2. Structural & Functional Annotation
  │     ├─► Sequence Length: Total amino acids (aa)
  │     ├─► Functional Domains: Zinc finger, kinase catalytic domain, transmembrane helices
  │     ├─► Active Sites: Catalytic dyads/triads, metal-binding residues, phosphorylation sites (PTMs)
  │     └─► Quaternary Structure: Monomer, homodimer, heterotetramer
  │
  ├── 3. Quantitative Physicochemical Evaluation
  │     └─► Execute `python_eval` to compute:
  │           • Exact Molecular Weight (kDa) from sequence stoichiometry
  │           • Theoretical Isoelectric Point (pI)
  │           • Molar Extinction Coefficient ($\epsilon_{280}$)
  │           • Grand Average of Hydropathy (GRAVY index)
  │
  ├── 4. Structural Verification
  │     ├─► PDB Cross-reference: High-resolution X-ray crystallographic or Cryo-EM coordinates
  │     └─► AlphaFold DB: pLDDT confidence scores for disordered regions
  │
  └── 5. Literature Correlation
        └─► Query `europe_pmc_search(query="<ACCESSION> OR (<GENE> AND structure)")`
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Cause | Remediation Action | Example |
| :--- | :--- | :--- | :--- |
| **0 hits on gene symbol** | Non-standard alias or vernacular name | Map through HGNC / UniProt alias search | `p53` $\rightarrow$ `gene:TP53` or `cellular tumor antigen p53` |
| **Multiple accessions returned** | Isoforms or multi-species homologs | Filter by canonical Swiss-Prot reviewed status (`reviewed:true`) | `TP53 AND reviewed:true AND organism_id:9606` |
| **Unmapped orphan sequence** | Synthetic construct or fusion protein | Split sequence into domain fragments or query parent scaffold | Query individual catalytic domain sequences |
| **Missing crystal structure** | Membrane protein or intrinsically disordered | Consult AlphaFold DB confidence scores or homologous templates | Cross-reference with mammalian ortholog structures |

---

## 4. Quantitative Protein Calculations (`python_eval`)

Never estimate molecular weights or extinction coefficients. Use `python_eval` with precise amino acid constants:

### A. Molecular Weight and Molar Extinction Coefficient ($\epsilon_{280}$)
```python
# Standard amino acid molecular weights (minus H2O condensation: 18.015 Da)
aa_weights = {
    'A': 71.08, 'R': 156.20, 'N': 114.11, 'D': 115.09, 'C': 103.14,
    'E': 129.12, 'Q': 128.13, 'G': 57.05,  'H': 137.14, 'I': 113.17,
    'L': 113.17, 'K': 128.18, 'M': 131.21, 'F': 147.18, 'P': 97.12,
    'S': 87.08,  'T': 101.11, 'W': 186.21, 'Y': 163.18, 'V': 99.13
}
sequence = "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP"  # Example N-term TP53
mw = sum(aa_weights.get(aa, 110.0) for aa in sequence) + 18.015
# Extinction coefficient at 280 nm (Pace et al.): E280 = 5500*Trp + 1490*Tyr + 125*Cys
nW = sequence.count('W')
nY = sequence.count('Y')
nC = sequence.count('C')
e280 = 5500 * nW + 1490 * nY + 125 * nC
print(f"Length: {len(sequence)} aa | MW: {mw/1000:.2f} kDa | E280: {e280} M^-1 cm^-1")
```

### B. Charge and Net Hydropathy (GRAVY Index)
```python
# Kyte-Doolittle hydropathy scale
hydropathy = {
    'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
    'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
    'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
    'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
}
gravy = sum(hydropathy.get(aa, 0.0) for aa in sequence) / len(sequence)
print(f"GRAVY Score: {gravy:.3f} ({'Hydrophobic' if gravy > 0 else 'Hydrophilic'})")
```

---

## 5. Proteomic Annotation Output Schema

Present analyzed proteins in this standard evidence table:

| Gene Symbol | Canonical UniProt ID | Organism | Length (aa) | Molecular Weight | Key Functional Domains | Catalytic / Active Sites | PDB / AF Structure |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TP53 | P04637 | *Homo sapiens* | 393 aa | 43.65 kDa | Transactivation (1-61), DNA-binding (102-292), Tetramerization (325-356) | Ser15/20 phosphorylation, Cys176/238/242 Zn-coordination | 1TUP (2.2 Å), AF-P04637 |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Confuse Canonical Isoform with Splice Variants**: UniProt default sequences represent Isoform 1 (canonical). If referring to a variant, state the exact isoform suffix (e.g. `P04637-2`).
2. **Never Fabricate Active Site Residue Coordinates**: Never guess numbering (e.g., calling catalytic Asp "Asp102" without checking the specific isoform sequence offset).
3. **Distinguish Experimental Structures from Predictions**: Always clarify whether a structure originates from high-resolution Cryo-EM / X-ray crystallography (PDB) or an *in silico* model (AlphaFold / ESMFold).
4. **Preserve Sequence Letters**: Use uppercase standard 20 IUPAC amino acid single-letter codes; disallow ambiguous characters (`X`, `B`, `Z`) unless noting uncharacterized residues.
