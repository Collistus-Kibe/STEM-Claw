---
name: arxiv-physics-literature
description: Rapid discovery, mathematical synthesis, and citation mapping for arXiv preprints across physics, condensed matter, and quantum systems.
category: physical_sciences
allowed_tools:
  - arxiv_search
  - openalex_search
  - crossref_search
  - search_local_papers
  - export_bibtex
  - python_eval
required_keys: []
priority: 1
version: "2.0.0"
tags:
  - arxiv
  - quantum-physics
  - preprints
  - mathematical-physics
  - cond-mat
upstream: "K-Dense-AI/scientific-agent-skills"
---

# arXiv Physics & Mathematical Literature Discovery

## 1. Overview & Objectives
arXiv is the primary preprint repository for physics, mathematics, and quantum computing. This skill standardizes taxonomy mapping, mathematical equation extraction, citation cross-referencing via OpenAlex, and archival into `references.bib`.

---

## 2. Subject Taxonomy & Category Routing
When querying arXiv, map domain problems to primary category prefixes:

| Physics Domain | arXiv Category Code | Core Topics |
|---|---|---|
| **Quantum Physics** | `quant-ph` | Quantum circuits, fault tolerance, Rydberg atoms, quantum optics |
| **Strongly Correlated Matter** | `cond-mat.str-el` | High-Tc superconductors, fractional Hall effect, Mott insulators |
| **Materials Science** | `cond-mat.mtrl-sci` | Density functional theory (DFT), perovskites, 2D materials |
| **High Energy Theory** | `hep-th` | String theory, AdS/CFT, quantum field theory, conformal bootstrap |
| **Astrophysics & Cosmology** | `astro-ph.CO` | Dark matter candidates, CMB anomalies, gravitational waves |
| **Chemical Physics** | `physics.chem-ph` | Molecular dynamics, vibrational spectroscopy, non-adiabatic dynamics |

---

## 3. Procedural Workflow

```
[Physics Concept / Hamiltonian]
        │
        ▼
[Step 1: Check Local Cache via `search_local_papers`]
        │
        ▼
[Step 2: Formulate Category-Scoped Query for `arxiv_search`]
        │
        ├──► If 0 Hits: Broaden query by dropping subcategory or quotes
        │
        ▼
[Step 3: Cross-Reference Global Citation Count via `openalex_search`]
        │
        ▼
[Step 4: Extract Theoretical Formalism & Quantitative Benchmarks]
        │
        ▼
[Step 5: Verify Numerical Calculations via `python_eval`]
        │
        ▼
[Step 6: Invoke `export_bibtex` with arXiv ID and Primary Class]
```

### Step 1: Query Formulation
- Include canonical operators or states: `all:("Majorana zero modes" AND "nanowire")` or `cat:quant-ph AND "surface code"`.
- Use `arxiv_search(query=..., limit=8)`.

### Step 2: Formalism & Equation Extraction
For theoretical studies, isolate:
- **Hamiltonian / Governing Equation**: Explicitly write Hamiltonians in LaTeX (e.g. $H = \sum_{i} J S_i \cdot S_{i+1}$).
- **Approximations**: Mean-field, perturbation order, LDA/GGA exchange-correlation functional, or tensor network bond dimension $\chi$.
- **Experimental System**: Superconducting qubits, trapped ions, diamond NV centers, synchrotron X-ray diffraction.

### Step 3: Numerical Sanity Verification
- If papers report gate fidelities (e.g. $99.92\%$), coherence times ($T_1, T_2^*$), or transition temperatures ($T_c$), use `python_eval` to calculate error budgets ($1 - F$), fidelity improvements, or critical scaling exponents.

### Step 4: BibTeX Archival
- Call `export_bibtex(arxiv_id='...', title='...', authors='...', year=...)` to log entry to `references.bib`.

---

## 4. Evidence Presentation Schema

```markdown
### Theoretical Model & Consensus
[Concise summary of physical mechanism, symmetry group, and Hamiltonian]

### Mathematical Formalism & Key Equation
$$
\hat{H} = \sum_{\langle i,j \rangle} -t (c_i^\dagger c_j + \text{h.c.}) + U \sum_i n_{i\uparrow} n_{i\downarrow}
$$

### Benchmark Matrix
| Study | Platform / Lattice | Parameter / Threshold | Physical Metric | arXiv Reference |
|---|---|---|---|---|
| Google Quantum AI (2023) | Superconducting Transmon | Surface code distance $d=5$ | $\Lambda = 0.107\%$ below threshold | arXiv:2207.06431 |

### Critical Physical Limitations
- [Decoherence channel, finite-size effect, or experimental temperature constraints]
```
