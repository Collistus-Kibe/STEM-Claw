---
name: ml-benchmark-comparison
description: Compare machine learning model architectures, leaderboard benchmarks, evaluation protocols, and SOTA results using Papers with Code and Semantic Scholar.
category: engineering_cs
allowed_tools:
  - papers_with_code
  - semantic_scholar_search
  - semantic_scholar_refs
  - github_search
  - export_bibtex
  - python_eval
  - search_local_papers
required_keys: []
priority: 10
version: "2.0.0"
tags:
  - machine-learning
  - benchmarks
  - leaderboards
  - papers-with-code
  - evaluation
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Machine Learning Benchmark Comparison & Evaluation Protocol

## 1. Overview & Objectives
This skill directs rigorous, reproducible benchmarking across machine learning architectures, evaluation datasets, and leaderboards. It prevents cherry-picked metric reporting, audits parameter counts, checks code availability, and catalogs citations.

---

## 2. Procedural Workflow

```
[ML Task / Model Architecture / Dataset]
        │
        ▼
[Step 1: Check Local Cache via `search_local_papers`]
        │
        ▼
[Step 2: Map Task to Standard Taxonomy (e.g. MMLU, GSM8K, ImageNet)]
        │
        ▼
[Step 3: Query Leaderboards via `papers_with_code(query=...)`]
        │
        ▼
[Step 4: Check Open-Source Code via `github_search(query=...)`]
        │
        ▼
[Step 5: Verify Baseline Publication & Citation Graph via `semantic_scholar_search`]
        │
        ▼
[Step 6: Compute Relative Gains & Parameter Efficiency via `python_eval`]
        │
        ▼
[Step 7: Produce Benchmark Comparison Table & Call `export_bibtex`]
```

### Step 1: Benchmark Taxonomy Disambiguation
Ensure the evaluation benchmark and split are precisely defined:
- **Language / Reasoning**: MMLU (5-shot), GSM8K (8-shot CoT), MATH, HumanEval (Pass@1), ARC-Challenge.
- **Computer Vision**: ImageNet Top-1, MS COCO (mAP@[.5:.95]), ADE20K (mIoU).
- **Multimodal**: MMMU, MathVista, VQA-v2.

### Step 2: Evaluation Hygiene Checklist
Before reporting a leaderboard metric, verify:
- **Prompt Setting**: Zero-shot, Few-shot (specify $k$), or Chain-of-Thought (CoT).
- **Compute & Parameter Scale**: Active parameters vs Total parameters (MoE vs Dense).
- **Data Contamination Checks**: Note if the publication conducted $n$-gram decontamination against test splits.

### Step 3: Quantitative Delta Calculation
Always use `python_eval` to compute exact improvements rather than guessing:
$$
\text{Relative Error Reduction} = \frac{\text{Baseline Error} - \text{Model Error}}{\text{Baseline Error}} \times 100\%
$$

### Step 4: Archival
For the leading architecture and baseline paper:
- Call `export_bibtex` to add both citations into `references.bib`.

---

## 3. Benchmark Comparison Schema

```markdown
### Benchmark Synthesis: [Task Name] (Dataset: [Dataset Name])

| Model Architecture | Parameter Scale | Evaluation Setup | Primary Metric (Score) | Relative Gain | Code Repository |
|---|---|---|---|---|---|
| DeepSeek-R1 | 671B (37B active) | Pass@1 (Greedy CoT) | MATH-500: 97.3% | +14.2% vs Baseline | [GitHub](https://...) |
| Qwen-2.5-72B-Instruct | 72B Dense | 5-shot CoT | MATH-500: 83.1% | Baseline | [GitHub](https://...) |

### Efficiency & Compute Trade-Off Analysis
- **Inference Flops**: [Active parameter throughput comparison]
- **Hardware Footprint**: [VRAM requirement, e.g. FP8 / 4-bit quantization support]

### Reproducibility Verification
- [Status of open weights, training recipes, and test harness availability]
```

---

## 4. Anti-Patterns & Negative Constraints
- ❌ **NEVER compare zero-shot with few-shot scores**: Always label prompt settings explicitly.
- ❌ **Do not compare total parameter count of MoE models to dense models directly**: Always state active parameters per token.
- ❌ **Do not omit benchmark dataset version**: E.g., HumanEval vs HumanEval+ or MMLU vs MMLU-Pro.
