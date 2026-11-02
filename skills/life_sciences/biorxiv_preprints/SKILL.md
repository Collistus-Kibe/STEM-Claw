---
name: biorxiv-preprint-radar
description: Discover early-stage biomedical preprints, computational biology breakthroughs, and emerging life sciences disclosures before formal peer review.
category: life_sciences
allowed_tools:
  - biorxiv_search
  - europe_pmc_search
  - search_local_papers
  - export_bibtex
  - format_citation
required_keys: []
priority: 3
version: "2.0.0"
tags:
  - biorxiv
  - preprints
  - early-discovery
  - genomics
upstream: "K-Dense-AI/scientific-agent-skills"
---

# bioRxiv Preprint Radar & Early-Stage Research Discovery

## 1. Overview & Objectives
bioRxiv hosts pre-peer-review manuscripts, offering a 6 to 18-month head start on cutting-edge discoveries in genomics, synthetic biology, structural biology, and bioinformatics. This skill directs systematic preprint harvesting, methodological sanity checks, and explicit disclosure tagging.

---

## 2. Procedural Workflow

```
[Target Topic / Gene / Pathway]
        │
        ▼
[Step 1: Check Local Cache via `search_local_papers`]
        │
        ▼
[Step 2: Define Temporal Horizon (Default: 30-90 Days)]
        │
        ▼
[Step 3: Execute `biorxiv_search(query=..., days_back=60, limit=8)`]
        │
        ├──► If 0 Hits: Broaden query keywords or extend `days_back` to 180
        │
        ▼
[Step 4: Cross-Examine Emerging Hypotheses vs Europe PMC Preprints]
        │
        ▼
[Step 5: Tabulate Preprints with Preliminary Disclosure Disclaimers]
        │
        ▼
[Step 6: Invoke `export_bibtex(venue='bioRxiv')` to Catalog Citations]
```

### Step 1: Temporal Scoping
Preprints age rapidly. Always choose an appropriate lookback window:
- **Emerging Breakouts**: `days_back=30`
- **Comprehensive Subject Survey**: `days_back=90` to `180`

### Step 2: Query Refinement
- bioRxiv API performs substring matching on title and abstract text.
- Use canonical acronyms alongside expanded terms: `AAV capsid engineering` or `alphafold single sequence`.

### Step 3: Zero-Hit Fallback
If bioRxiv search returns empty:
1. Increase `days_back` parameter (e.g. from 30 to 180 days).
2. Fall back to `europe_pmc_search(query='...')` filtering for preprint archives (Europe PMC aggregates bioRxiv and medRxiv).

### Step 4: Methodological Scrutiny
Because preprints have not completed peer review, evaluate:
- **Sample Size / Replicates**: Look for biological vs technical replicates ($N \ge 3$).
- **Statistical Controls**: Note whether negative/scramble controls or wild-type baselines were tested.
- **Code/Data Availability**: Check if GitHub links or Zenodo accession IDs are provided in the abstract.

---

## 3. Structured Preprint Synthesis Schema

```markdown
### ⚠️ Preliminary Research Notice
*The following discoveries are preliminary preprints from bioRxiv that have not undergone formal peer review. Findings should be evaluated critically.*

### Emerging Research Radar
| Title & Date | Authors & Lab | Proposed Innovation / Mechanism | Replicates & Data | bioRxiv DOI |
|---|---|---|---|---|
| Deep generative design of binders (2024-03) | Watson et al. | RFdiffusion de novo design | N=24 designs, SPR verified | 10.1101/2024... |

### Key Technological Trends
- [Emerging paradigm observed across the harvested preprints]
```

---

## 4. Anti-Patterns & Constraints
- ❌ **NEVER present preprint claims as settled facts**: Always use language such as *"Authors propose..."* or *"Preliminary preprint data suggests..."*.
- ❌ **Do not omit the bioRxiv DOI**: Preprints frequently update versions (v1, v2); the canonical DOI ensures version traceability.
- ❌ **Always archive**: Proactively call `export_bibtex` with `venue='bioRxiv'` to save citekeys into `references.bib`.
