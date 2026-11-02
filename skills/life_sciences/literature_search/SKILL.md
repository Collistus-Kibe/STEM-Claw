---
name: literature-search-pubmed
description: Systematic biomedical literature search, MeSH ontology mapping, and abstract extraction across NCBI PubMed and Europe PMC.
category: life_sciences
allowed_tools:
  - ncbi_esearch
  - ncbi_efetch
  - europe_pmc_search
  - search_local_papers
  - export_bibtex
  - format_citation
required_keys: []
priority: 1
version: "2.0.0"
tags:
  - pubmed
  - literature
  - biomedical
  - mesh
  - citations
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Literature Search — PubMed & Europe PMC

## 1. Overview & Objectives
This skill governs exhaustive, evidence-based harvesting of biomedical literature across NCBI Entrez PubMed and Europe PMC. It enforces strict provenance, prevents hallucination of citation IDs, and maintains the project's `references.bib` automatically.

---

## 2. Decision Tree & Procedural Workflow

```
[User Query / Topic]
        │
        ▼
[Step 1: Check Local Cache via `search_local_papers`]
        │
        ├──► Matches Found? (Synthesize instantly without network roundtrips)
        │
        ▼
[Step 2: Formulate MeSH & Boolean Query for NCBI Entrez]
        │
        ▼
[Step 3: Execute `ncbi_esearch(query=..., limit=10)`]
        │
        ├──► If 0 Hits: Run Adaptive Query Recovery (Step 3a)
        │
        ▼
[Step 4: Fetch Detailed Abstracts via `ncbi_efetch(id=...)`]
        │
        ▼
[Step 5: Check European Open-Access / Preprints via `europe_pmc_search`]
        │
        ▼
[Step 6: Synthesize Evidence Matrix & Call `export_bibtex`]
```

### Step 1: Local Cache Probe
Before triggering external API calls, invoke `search_local_papers(query=...)`. If high-confidence matches exist from prior research turns, integrate them first.

### Step 2: Query Formulation & MeSH Expansion
Transform natural language into canonical biomedical terms:
- Combine specific genes/proteins with biological phenomena: `(Cas9 OR "CRISPR-associated protein 9") AND ("off-target" OR fidelity)`.
- Use MeSH equivalents when searching diseases or mechanisms (e.g. `Neoplasms` for cancer, `Apoptosis` for cell death).

### Step 3: Zero-Hit Adaptive Recovery Protocol
If `ncbi_esearch` returns `0` results:
1. Strip strict Boolean quotes (e.g. change `"base editing in vivo"` to `base editing in vivo`).
2. Remove temporal boundaries or narrow qualifiers.
3. Fall back to `europe_pmc_search` which indexes broader European institutional repositories and preprints.

### Step 4: Evidence Extraction Standards
From retrieved abstracts, strictly isolate:
- **Experimental System**: In vitro (biochemical assay), Ex vivo (cell lines), In vivo (animal models: Mus musculus, Danio rerio), or Human Clinical Trial (Phase I-IV).
- **Primary Mechanism**: Molecular pathway, receptor target, or catalytic mode.
- **Quantitative Metrics**: $IC_{50}$, binding affinity $K_d$, fold-change, p-value ($p < 0.05$).

### Step 5: Archival
For every pivotal paper discovered:
- Invoke `export_bibtex` to append the standardized citation to `references.bib`.

---

## 3. Evidence Synthesis Template
When presenting literature findings to the researcher, use this structured schema:

```markdown
### Primary Scientific Consensus
[Direct 2-3 sentence answer synthesizing the prevailing biological mechanism]

### Verified Evidence Matrix
| Study & Year | Model / System | Mechanism / Target | Key Empirical Metric | Provenance |
|---|---|---|---|---|
| Ran et al. (2015) | Human HEK293T cells | SpCas9 high-fidelity engineering | 85% on-target / 0% detectable off-target | PMID: 26628643 |

### Methodological Limitations & Open Questions
- [Key experimental constraint, sample size limitation, or biological confounder]
```

---

## 4. Anti-Patterns & Negative Constraints
- ❌ **NEVER fabricate PMIDs or DOIs**: If an identifier is missing from the database record, explicitly declare `[DOI: Unavailable]`.
- ❌ **NEVER conflate in vitro findings with clinical efficacy**: Clearly label cell culture vs living animal vs human trials.
- ❌ **Do not treat correlation as causation**: Differentiate between statistical biomarkers and mechanistic driver mutations.
