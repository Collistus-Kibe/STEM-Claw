---
name: "code-architecture-inspection"
description: "Analyze open-source repository structures, code implementations, software dependencies, and reproducibility using GitHub search and local file tools."
category: "engineering_cs"
allowed_tools:
  - github_search
  - suggest_repo
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 20
version: "2.0.0"
tags:
  - github
  - software-engineering
  - code-architecture
  - reproducibility
  - open-source
  - machine-learning-systems
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Code Architecture & Open-Source Inspection Protocol

## 1. Overview & Systems Scope
This protocol governs the identification, static architectural analysis, modular decomposition, and reproducibility audit of open-source research implementations. It evaluates official codebases, checks build and dependency specifications (`pyproject.toml`, `requirements.txt`, `Cargo.toml`), audits open-source licenses, and maps out component interactions.

---

## 2. Decision Tree & Codebase Audit Pipeline

```
User Query (Algorithm / Framework / Model Name / GitHub Repo)
  │
  ├── 1. Repository Identification via GitHub API
  │     └─► Invoke `github_search(query="<MODEL_OR_ALGORITHM> official", limit=5)`
  │           ├─► Hit: Extract full_name, stargazers_count, default_branch, description, license
  │           └─► Ambiguous/Miss: Consult `suggest_repo(topic="...")` for curated category repos
  │
  ├── 2. Verification of Canonical Authorship
  │     ├─► Official Author/Institution Match: Matches paper authors (e.g. meta-llama, huggingface, openai)
  │     ├─► Community Port / Unofficial: Disclose if repository is a third-party re-implementation
  │     └─► Activity & Maintenance: Check latest commit date, open issues, and stars
  │
  ├── 3. Directory Layout & Modular Decomposition
  │     ├─► Packaging & Build: pyproject.toml, setup.py, Dockerfile, CMakeLists.txt
  │     ├─► Core Modeling: Model definition scripts (`models/`, `architecture.py`)
  │     ├─► Training & Inference: `train.py`, `inference.py`, `eval.py`
  │     └─► Test Harness: `tests/`, continuous integration (`.github/workflows`)
  │
  ├── 4. Dependency & Hardware Requirements
  │     ├─► Framework: PyTorch, JAX, TensorFlow, Rust, C++ CUDA
  │     ├─► Hardware Accelerators: GPU VRAM thresholds (e.g. 16GB, 80GB A100), FP8/INT4 quantization
  │     └─► Licensing: Permissive (MIT, Apache 2.0, BSD) vs Copyleft (GPL v3) vs Research-Only
  │
  └── 5. Quantitative Computational Complexity (`python_eval`)
        └─► Calculate parameter scaling, FLOPs per token ($6ND$), and memory footprints
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Cause | Remediation Action | Example Query |
| :--- | :--- | :--- | :--- |
| **0 hits on algorithm acronym** | Generic or ambiguous name | Combine author name or venue with keyword | `Mamba` $\rightarrow$ `state spaces Albert Gu Mamba official` |
| **Too many low-quality forks returned** | Unranked keyword search | Filter by star threshold or fork count in GitHub search | `sort:stars stars:>100 <query>` |
| **No code published by authors** | Proprietary or closed-source paper | Search for high-starred community reproduction or Papers With Code | `open-source reproduction <method>` |
| **Missing license file** | License unspecified in root | Inspect header comments of core source files or setup files | Check `LICENSE`, `COPYING`, or `setup.cfg` |

---

## 4. Quantitative Systems Calculations (`python_eval`)

Never estimate model parameters or GPU memory footprints. Calculate them with `python_eval`:

### A. Transformer Parameter and VRAM Footprint Estimation
```python
def estimate_transformer_vram(params_billion: float, precision_bytes: int = 2, context_tokens: int = 4096, batch_size: int = 1):
    """Estimate inference VRAM footprint in Gigabytes."""
    # Weights memory
    weights_gb = (params_billion * 1e9 * precision_bytes) / (1024 ** 3)
    # KV cache approximation (for typical 32-layer, 32-head, head_dim=128 model)
    # KV cache = 2 * n_layers * n_heads * head_dim * context * precision * batch
    kv_cache_bytes = 2 * 32 * 32 * 128 * context_tokens * precision_bytes * batch_size
    kv_cache_gb = kv_cache_bytes / (1024 ** 3)
    # Activation & CUDA runtime overhead
    overhead_gb = 1.5
    total_gb = weights_gb + kv_cache_gb + overhead_gb
    print(f"Model Size: {params_billion}B | Precision: {precision_bytes*8}-bit")
    print(f"Weights: {weights_gb:.2f} GB | KV Cache ({context_tokens} ctx): {kv_cache_gb:.2f} GB")
    print(f"Total Inference VRAM: {total_gb:.2f} GB")

# Example: 8B model in FP16 (2 bytes) vs FP8 (1 byte)
estimate_transformer_vram(params_billion=8.0, precision_bytes=2)
print("---")
estimate_transformer_vram(params_billion=8.0, precision_bytes=1)
```

### B. Training FLOPs Estimation ($6ND$)
```python
def estimate_training_flops(params_billion: float, tokens_trillion: float) -> str:
    """Kaplan et al. / Chinchilla 6 * N * D formulation for training compute."""
    n = params_billion * 1e9
    d = tokens_trillion * 1e12
    total_flops = 6 * n * d
    zettaflops = total_flops / 1e21
    return f"Total Training Compute: {total_flops:.2e} FLOPs ({zettaflops:.2f} ZettaFLOPs)"

# Example: LLaMA-3 8B trained on 15T tokens
print(estimate_training_flops(params_billion=8.0, tokens_trillion=15.0))
```

---

## 5. Code Architecture Evidence Matrix Output Schema

Summarize inspected repositories using this structured table:

| Repository Name | GitHub URL | Stars / Activity | Official Authorship | Core Framework | License | Reproducibility Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `state-spaces/mamba` | `https://github.com/state-spaces/mamba` | 13.5k+ (Active) | Yes (Albert Gu, Tri Dao) | PyTorch / Triton CUDA | Apache-2.0 | High (pip installable, pre-trained weights on HF) |
| `vllm-project/vllm` | `https://github.com/vllm-project/vllm` | 32.0k+ (Active) | Yes (UC Berkeley) | C++ / PyTorch / CUDA | Apache-2.0 | Production-grade (PagedAttention, Docker image) |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Assume Canonical Ownership Without Verification**: Cross-check organization name with paper institutions (e.g. verify if repo is from `google-research`, `meta-llama`, or an unrelated student project).
2. **Never Fabricate File Paths**: Only reference file paths (`models/transformer.py`) that exist in the repository tree.
3. **Disclose License Copyleft Implications**: If an implementation uses GPL v3 or AGPL, explicitly notify the researcher of viral copyleft constraints before adopting into commercial pipelines.
4. **BibTeX Archiving**: Proactively export citation metadata for software papers via `export_bibtex`.
