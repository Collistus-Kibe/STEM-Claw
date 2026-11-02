---
name: systematic-literature-review
description: Execute PRISMA-compliant multi-repository systematic searches, deduplication, and evidence synthesis across cross-disciplinary scientific databases.
category: interdisciplinary
allowed_tools:
  - core_search
  - doaj_search
  - zenodo_search
  - osf_preprints
  - unpaywall_lookup
  - export_bibtex
  - search_local_papers
  - python_eval
required_keys: []
priority: 10
version: "2.0.0"
tags:
  - systematic-review
  - prisma
  - meta-analysis
  - cross-disciplinary
  - deduplication
upstream: "K-Dense-AI/scientific-agent-skills"
---

# PRISMA Systematic Literature Review & Evidence Synthesis

## 1. Overview & Objectives
This skill governs structured, bias-resistant literature surveys adhering to PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) principles across open access journals, grey literature, and preprints.

---

## 2. PRISMA Methodological Pipeline

```
[Research Question & PICO Protocol]
        │
        ▼
[Phase 1: Identification]
  ├── Query Peer-Reviewed Open Access (`doaj_search`, `core_search`)
  ├── Query Multidisciplinary Preprints (`osf_preprints`)
  └── Query Research Data & Grey Literature (`zenodo_search`)
        │
        ▼
[Phase 2: Screening & Deduplication]
  ├── Canonical DOI matching across repositories
  └── Title string distance normalization
        │
        ▼
[Phase 3: Eligibility & Full-Text Retrieval]
  └── Resolve Legal OA PDFs via `unpaywall_lookup(doi=...)`
        │
        ▼
[Phase 4: Synthesis & Meta-Analysis]
  ├── Quantitative extraction of effect sizes, risk ratios, or metrics
  ├── Statistical verification via `python_eval`
  └── Batch citation export to `references.bib` via `export_bibtex`
```

### Phase 1: Query Protocol Formulation
Structure search queries using the **PICO** or **CIMO** framework:
- **P** (Population / Problem): Domain system under observation.
- **I** (Intervention / Technology): Method, architecture, or chemical treatment applied.
- **C** (Comparator): Baseline model, control group, or wild-type.
- **O** (Outcome): Primary measured empirical variable.

### Phase 2: Deduplication Rules
When combining records across CORE, DOAJ, and OSF:
1. Normalize DOI strings to lowercase without URL prefixes.
2. If DOI is missing, compute similarity on alphanumeric title tokens.
3. If duplicate found, prioritize peer-reviewed record over preprint version.

### Phase 3: Evidence Extraction & Meta-Analysis
For each included study, isolate:
- Study Design (RCT, cohort, observational, computational simulation)
- Sample Size ($N$)
- Primary Metric & Uncertainty Interval (95% CI, standard error)
- Quality / Risk of Bias Assessment (Low, Medium, High risk)

---

## 3. PRISMA Evidence Synthesis Schema

```markdown
### PRISMA Flow Summary
- **Total Records Identified**: N = [Count] across [CORE, DOAJ, OSF, Zenodo]
- **Duplicates Removed**: N = [Count]
- **Studies Evaluated in Full**: N = [Count]

### Comprehensive Evidence Synthesis Table
| Study & Year | Field / Domain | Methodology & Sample Size | Primary Outcome / Finding | Risk of Bias | DOI / Access |
|---|---|---|---|---|---|
| Zhang et al. (2023) | Bio-Informatics | Multi-cohort benchmarking (N=1,200) | 94.2% agreement with gold standard | Low Risk | [DOAJ / Link] |

### Cross-Disciplinary Insights & Gaps
- **Convergence**: [Points of consensus across diverse domains]
- **Divergence / Contradictions**: [Conflicting results and methodological causes]
- **Research Gap**: [Identified blind spots requiring future empirical study]
```

---

## 4. Anti-Patterns & Constraints
- ❌ **NEVER rely on a single database**: A valid systematic review must search at least two complementary repositories.
- ❌ **Do not ignore negative or null results**: Publication bias skews positive results; actively record studies finding no statistically significant effect.
- ❌ **Maintain bibliography**: Always catalog included studies via `export_bibtex`.
