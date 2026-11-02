---
name: "clinical-trials-lookup"
description: "Search translational clinical investigations, efficacy outcomes, Kaplan-Meier survival, and therapeutic protocols."
category: "life_sciences"
allowed_tools:
  - europe_pmc_search
  - ncbi_esearch
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 4
version: "2.0.0"
tags:
  - clinical-trials
  - medicine
  - therapeutics
  - oncology
  - randomized-controlled-trials
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Clinical Trials & Translational Medicine Protocol

## 1. Overview & Clinical Scope
This protocol governs the investigation of human clinical trials, therapeutic interventions, phase progression, and translational oncology/pharmacology benchmarks. It enforces strict clinical evidence hierarchies, endpoint extraction rigor, and mathematical verification of statistical efficacy metrics.

---

## 2. Decision Tree & Clinical Trial Triage

```
User Query (Disease + Intervention + Phase)
  │
  ├── 1. Check Local Cache
  │     └─► `search_local_papers(query="<intervention> <disease> clinical trial")`
  │           ├─► Hit: Extract registry ID (NCT#), Phase, Cohort, Primary Endpoint
  │           └─► Miss: Proceed to step 2
  │
  ├── 2. Formulate Structured MeSH / Europe PMC Query
  │     └─► Europe PMC: `(TITLE:"<intervention>") AND ("clinical trial" OR "randomized")`
  │     └─► PubMed / NCBI: `"<intervention>"[tiab] AND "<disease>"[tiab] AND (clinical trial[pt] OR randomized controlled trial[pt])`
  │
  ├── 3. Trial Classification & Study Phase
  │     ├─► Phase I: Safety, maximum tolerated dose (MTD), dose-limiting toxicities (DLTs), pharmacokinetics
  │     ├─► Phase II: Biological activity, response rate (ORR), proof-of-concept, optimal dosing
  │     ├─► Phase III: Pivotal comparative efficacy vs Standard of Care (SoC), randomized double-blind
  │     └─► Phase IV: Post-marketing pharmacovigilance, long-term real-world evidence (RWE)
  │
  ├── 4. Primary Endpoint Verification
  │     ├─► Time-to-Event: Overall Survival (OS), Progression-Free Survival (PFS), Disease-Free Survival (DFS)
  │     ├─► Binary/Categorical: Objective Response Rate (ORR), Complete Response (CR), Pathologic CR (pCR)
  │     └─► Safety/Toxicity: CTCAE Grade 3/4 treatment-emergent adverse events (TEAEs)
  │
  └── 5. Quantitative Verification
        └─► Use `python_eval` to calculate:
              • Absolute Risk Reduction: $ARR = |CER - EER|$
              • Number Needed to Treat: $NNT = 1 / ARR$
              • Hazard Ratio 95% Confidence Interval width and symmetry
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

When querying clinical trial endpoints, if zero results are returned, execute the following staged fallback:

| Stage | Trigger | Action | Example Query |
| :--- | :--- | :--- | :--- |
| **Stage 1** | Strict Phase string returns 0 hits | Drop Roman numerals and search trial keywords | Replace `Phase III pembrolizumab NSCLC` $\rightarrow$ `pembrolizumab "non-small cell lung cancer" trial` |
| **Stage 2** | Proprietary drug code yields 0 hits | Map developmental code to generic INN or target | Replace `MK-3475` $\rightarrow$ `pembrolizumab` OR `anti-PD-1` |
| **Stage 3** | Specific sub-indication yields 0 hits | Generalize disease phenotype to organ system | Replace `EGFR L858R NSCLC` $\rightarrow$ `EGFR-mutated lung adenocarcinoma` |
| **Stage 4** | Missing registry link in PMC | Query Europe PMC by NCT trial identifier | `INVESTIGATOR_ID:"NCT02578680"` or `EXT_ID:"NCT02578680"` |

---

## 4. Quantitative Clinical Calculations (`python_eval`)

Never estimate or guess statistical indicators. Execute exact calculations via `python_eval`:

### A. Number Needed to Treat (NNT)
```python
# Absolute Risk Reduction (ARR) and Number Needed to Treat (NNT)
control_event_rate = 0.28  # e.g., 28% recurrence in placebo/standard of care
experimental_event_rate = 0.16  # e.g., 16% recurrence in active arm
arr = control_event_rate - experimental_event_rate
nnt = 1.0 / arr if arr > 0 else float("inf")
print(f"ARR = {arr:.4f} ({arr*100:.1f}%), NNT = {round(nnt, 1)}")
```

### B. Hazard Ratio (HR) and Log-Rank SMR
```python
import math
# Verify 95% Confidence Interval log-symmetry
hr = 0.68
ci_lower = 0.53
ci_upper = 0.87
log_hr = math.log(hr)
log_lower = math.log(ci_lower)
log_upper = math.log(ci_upper)
se_lower = (log_hr - log_lower) / 1.96
se_upper = (log_upper - log_hr) / 1.96
print(f"Log(HR)={log_hr:.3f}, SE(lower)={se_lower:.3f}, SE(upper)={se_upper:.3f}")
```

---

## 5. Clinical Evidence Matrix Output Schema

Format extracted clinical findings using this exact markdown table:

| Trial Identifier | Phase | Intervention vs Control | Cohort ($N$) | Primary Endpoint Result | Adverse Events (Grade 3/4) | DOI / PMID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| NCT02578680 (KEYNOTE-042) | Phase III | Pembrolizumab vs Platinum Chemotherapy | 1274 | OS: HR 0.81 (95% CI 0.71–0.93, $p=0.0018$) | 18% vs 41% | 10.1016/S0140-6736(18)32409-7 |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Confuse Preclinical and Human Studies**: Never label cell line ($in\ vitro$) or murine xenograft ($in\ vivo$) experiments as clinical trials.
2. **Never Fabricate Trial Registry IDs**: If an NCT identifier (e.g. `NCT01234567`) is not explicitly stated in the paper text, declare `NCT: Unassigned / Institutional`.
3. **Report Intention-to-Treat (ITT)**: Always specify whether reported efficacy represents the Intention-to-Treat (ITT) population, Per-Protocol (PP), or Safety evaluable set.
4. **Distinguish Statistical vs Clinical Significance**: A statistically significant $p < 0.05$ with marginal median survival delta ($< 2$ weeks) must be contextualized with ASCO/ESMO clinical benefit framework thresholds.
5. **Continuous BibTeX Export**: When a pivotal Phase III landmark trial is confirmed, immediately call `export_bibtex` to persist the citation to `.stemclaw/references.bib`.
