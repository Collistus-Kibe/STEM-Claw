---
name: "open-access-fulltext-resolver"
description: "Resolve legal open-access full-text PDFs, institutional repository mirrors, preprint versions, and licensing for DOI references via Unpaywall."
category: "interdisciplinary"
allowed_tools:
  - unpaywall_lookup
  - suggest_repo
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 20
version: "2.0.0"
tags:
  - unpaywall
  - open-access
  - scholarly-publishing
  - full-text
  - doi
  - preprints
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Open Access Full-Text Resolver Protocol

## 1. Overview & Scholarly Scope
This protocol governs the automated discovery, legal open-access verification, and full-text retrieval of scientific publications using Unpaywall and scholarly identifiers. It classifies publications into canonical Open Access (OA) tiers, locates author accepted manuscripts (AAM) in institutional repositories, verifies Creative Commons licenses, and provides fallback pathways for paywalled literature.

---

## 2. Decision Tree & Open Access Pipeline

```
User Query (DOI String / Citation Reference)
  │
  ├── 1. Check Local Paper Cache
  │     └─► `search_local_papers(query="<DOI_OR_TITLE>")`
  │           ├─► Hit: Extract cached metadata and full text if stored
  │           └─► Miss: Proceed to step 2
  │
  ├── 2. Query Unpaywall API
  │     └─► Invoke `unpaywall_lookup(doi="10.xxxx/...")`
  │           ├─► Response: is_oa (True/False), oa_status, best_oa_location
  │           └─► Miss/Malformed DOI: Sanitize string (strip 'https://doi.org/')
  │
  ├── 3. OA Status Tier Classification
  │     ├─► Gold OA: Published in a fully open-access journal (e.g. PLOS, BMC, Nature Communications)
  │     ├─► Hybrid OA: Published in a subscription journal with an author-paid article processing charge (APC)
  │     ├─► Bronze OA: Free to read on publisher website, but lacks explicit Creative Commons re-use license
  │     ├─► Green OA: Self-archived accepted manuscript (AAM) in an institutional repository or preprint server
  │     └─► Closed: Strictly behind a commercial paywall
  │
  ├── 4. Primary Full-Text Link Extraction
  │     ├─► URL: `best_oa_location.url_for_pdf` (direct PDF download link)
  │     ├─► Landing Page: `best_oa_location.url_for_landing_page`
  │     └─► License: CC-BY, CC-BY-NC, CC-BY-SA, or publisher-specific terms
  │
  ├── 5. Fallback for Paywalled ("Closed") Literature
  │     ├─► Query preprint servers (arXiv, bioRxiv, medRxiv, OSF Preprints)
  │     ├─► Query OpenAlex / CORE / Europe PMC for author post-prints
  │     └─► Check institutional repositories (e.g. Harvard DASH, MIT Open Access Articles)
  │
  └── 6. Citation & Provenance Archiving
        └─► Call `export_bibtex` to persist canonical bibliographic entry
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Cause | Remediation Action | Example |
| :--- | :--- | :--- | :--- |
| **404 Not Found on DOI** | Leading URL schema or trailing punctuation in string | Strip prefixes like `https://doi.org/` or `doi:` and trailing dots | Replace `https://doi.org/10.1038/nature12373.` $\rightarrow$ `10.1038/nature12373` |
| **Closed access returned** | Publisher version paywalled | Search repository mirrors for Green OA author accepted manuscript (AAM) | Check `first_oa_location` or query CORE with article title |
| **PDF link returns 403 Forbidden** | Anti-scraping on publisher direct PDF link | Fall back to landing page URL or institutional repository mirror | Use `url_for_landing_page` or Europe PMC repository mirror |
| **No DOI available** | Title-only citation | Query Crossref or OpenAlex to resolve title to canonical DOI string | Resolve title via `crossref_search(query=...)` first |

---

## 4. Quantitative Scholarly Calculations (`python_eval`)

Never guess open access proportions or journal APC costs. Use `python_eval` for cohort metrics:

### A. Open Access Portfolio Proportion & Cost Analysis
```python
def analyze_oa_portfolio(papers: list):
    """Calculate open-access compliance ratios and distribution across tiers."""
    total = len(papers)
    counts = {"gold": 0, "hybrid": 0, "green": 0, "bronze": 0, "closed": 0}
    for p in papers:
        status = p.get("oa_status", "closed").lower()
        counts[status] = counts.get(status, 0) + 1
        
    oa_total = total - counts["closed"]
    oa_rate = (oa_total / total) * 100 if total > 0 else 0.0
    
    print(f"Total Papers Evaluated: {total}")
    print(f"Overall OA Rate: {oa_rate:.1f}% ({oa_total}/{total})")
    print(f"Tier Breakdown: Gold={counts['gold']}, Hybrid={counts['hybrid']}, Green={counts['green']}, Bronze={counts['bronze']}, Closed={counts['closed']}")

# Example portfolio
sample_records = [
    {"oa_status": "gold"}, {"oa_status": "gold"}, {"oa_status": "hybrid"},
    {"oa_status": "green"}, {"oa_status": "closed"}, {"oa_status": "closed"}
]
analyze_oa_portfolio(sample_records)
```

---

## 5. Open Access Evidence Matrix Output Schema

Present resolved publications in this standardized table:

| DOI | Article Title | OA Status | Direct PDF Link | Host Type | License | Institutional Repository Mirror |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `10.1038/s41586-020-2649-2` | Highly accurate protein structure prediction with AlphaFold | Gold | `https://www.nature.com/articles/s41586-021-03819-2.pdf` | Publisher | CC-BY 4.0 | Europe PMC (PMC8552697) |
| `10.1126/science.1257579` | Single-cell RNA-seq reveals dynamic, random monoallelic gene expression | Green | `https://dash.harvard.edu/bitstream/handle/1/13454656/...` | Repository | CC-BY | Harvard DASH / NIH-PA |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Label Paywalled Articles as Open Access**: If Unpaywall states `is_oa: false`, the paper must be reported as `Closed Access / Paywalled`.
2. **Never Fabricate PDF URLs**: Never construct arbitrary PDF URLs from guesswork. Only provide URLs returned by `unpaywall_lookup` or confirmed repository endpoints.
3. **Respect Creative Commons License Restrictions**: Always state if an article has non-commercial (`NC`) or no-derivatives (`ND`) clauses when recommending figures or dataset re-use.
4. **BibTeX Export**: Always persist canonical metadata using `export_bibtex` for subsequent citation in academic manuscripts.
