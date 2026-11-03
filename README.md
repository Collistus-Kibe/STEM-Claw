# STEMCLAW 🦀🔬

```text
  ███████╗████████╗███████╗███╗   ███╗  ██████╗██╗      █████╗ ██╗    ██╗
  ██╔════╝╚══██╔══╝██╔════╝████╗ ████║ ██╔════╝██║     ██╔══██╗██║    ██║
  ███████╗   ██║   █████╗  ██╔████╔██║ ██║     ██║     ███████║██║ █╗ ██║
  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║ ██║     ██║     ██╔══██║██║███╗██║
  ███████║   ██║   ███████╗██║ ╚═╝ ██║ ╚██████╗███████╗██║  ██║╚███╔███╔╝
  ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ 
                   A Scientific Research Agent for the IDE
```

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Model: Meta Model API](https://img.shields.io/badge/Model-Meta%20Model%20API-7928CA.svg)](https://dev.meta.ai/)
[![Architecture: Loadout System](https://img.shields.io/badge/Architecture-5%20STEM%20Loadouts-00DF72.svg)](#-5-stem-specialization-categories)
[![Live Endpoints: 29+](https://img.shields.io/badge/Endpoints-29%2B%20Live%20Scientific%20APIs-0070F3.svg)](#-complete-endpoint-directory-by-category)

**StemClaw** is an autonomous, skill-driven scientific research agent designed for pair programming and deep literature investigation directly inside your IDE terminal. Powered by the **Meta Model API** (`muse-wonder` and `muse-spark`), StemClaw features a **dynamic loadout architecture**: select your scientific domain at launch, and StemClaw arms the exact endpoint tools, curated knowledge repositories, and procedural skills required for your research.

---

## ⚡ Core Capabilities & Features

- **🎯 5 Specialization Loadouts**: Specializes context on demand across Life Sciences, Physical Sciences, Engineering & CS, Earth & Environmental, and Interdisciplinary Science.
- **🤖 Native Meta Model API Integration**:
  - `muse-wonder`: Frontier reasoning model for long-horizon planning, multi-step subagent delegation, and autonomous deep research.
  - `muse-spark`: Lightweight, ultra-fast model for rapid literature search, citation verification, and data parsing.
- **🌊 Long-Horizon Deep Research Engine (`/deep [goal]`)**:
  - Autonomous multi-epoch exploration running across minutes to hours.
  - Dynamically formulates hypotheses, executes targeted literature searches, extracts quantitative evidence into an Evidence Locker, and compiles publication-ready markdown (`report.md`), LaTeX (`research_paper.tex`), and BibTeX (`references.bib`) drafts.
- **🌐 29+ Live Scientific Endpoints**: Direct, unmocked integrations with NCBI/PubMed, bioRxiv, Europe PMC, UniProt, ChEMBL, PubChem, arXiv, Semantic Scholar, Crossref, OpenAlex, Unpaywall, GitHub, CORE, GBIF, USGS, NASA, and NOAA.
- **🔄 Cross-Category Tool Discovery**: Domain-specific tools can be cross-called seamlessly (e.g., querying ChEMBL from Life Sciences, or querying arXiv from Computer Science).
- **📚 Deterministic Citation Manager**:
  - `export_bibtex`: Appends standardized BibTeX entries with deterministic citekeys (`@article{vaswani2017attention}`).
  - `format_citation`: Formats paper citations instantly into APA 7th, IEEE, Nature, or Chicago styles.
- **💻 Scientific Python Sandbox & Data Profiler**:
  - `python_eval`: In-memory sandbox for statistical tests, mathematical computations, and data transformations.
  - `dataset_inspect`: Instant tabular summary (`.csv`, `.tsv`), JSON inspection, or genomic FASTA sequence profiling with GC-content calculation.
- **🛡️ Secret Isolation & Real-Time Asterisk Masking**:
  - Inputting keys is protected with real-time `*******` masking for typing, `Ctrl+V`, and right-click paste.
  - All API keys are isolated in local `.stemclaw/.env` files and **never** leaked into model context.
- **💾 Local SQLite Research Memory**:
  - Caches literature searches, abstracts, and DOIs locally to prevent redundant queries and save API rate limits.

---

## 🔬 5 STEM Specialization Categories

```text
┌────────────────────────── Box [1] • Life Sciences ──────────────────────────┐
│ Genomics • Proteomics • Molecular Biology • Biomedicine                     │
│ Endpoints: NCBI/PubMed • Europe PMC • bioRxiv • UniProtKB • Clinical Trials │
└─────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────── Box [2] • Physical Sciences ────────────────────────┐
│ Quantum • Chemistry • Condensed Matter • Materials Informatics              │
│ Endpoints: arXiv • OpenAlex • Crossref • DOE PAGES • ChEMBL • PubChem       │
└─────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────── Box [3] • Engineering & CS ─────────────────────────┐
│ Machine Learning • Systems Architecture • Algorithms • Reproducibility      │
│ Endpoints: Semantic Scholar • DBLP • Papers With Code • GitHub • IEEE       │
└─────────────────────────────────────────────────────────────────────────────┘
┌────────────────────── Box [4] • Earth & Environmental ──────────────────────┐
│ Biodiversity • Climate Records • Geospatial • Seismology                    │
│ Endpoints: GBIF Occurrences • NASA Open Data • NOAA Climate • USGS          │
└─────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────── Box [5] • Interdisciplinary ────────────────────────┐
│ Systematic Literature Reviews (PRISMA) • Open Science • Meta-Science        │
│ Endpoints: CORE API • Unpaywall (PDFs) • DOAJ • Zenodo • Figshare • OSF     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 Complete Endpoint Directory by Category

StemClaw features over 29 live scientific APIs wired directly into each loadout:

### Category 1: Life Sciences 🧬
*Focus: Molecular biology, genetics, bioinformatics, proteomics, and biomedicine.*
- **`ncbi_esearch`**: Query NCBI Entrez / PubMed databases by keyword, MeSH term, or author.
- **`ncbi_efetch`**: Retrieve full XML/abstract metadata for specific PubMed IDs (PMIDs) or GenBank accessions.
- **`europe_pmc_search`**: Search 40M+ life science articles, clinical guidelines, and preprints via Europe PMC.
- **`biorxiv_search`**: Live preprint search from bioRxiv and medRxiv across biology, genomics, and medicine.
- **`uniprot_search`**: Query UniProtKB for curated protein functional annotations, amino acid sequences, and PDB structures.
- **`orcid_lookup`**: Fetch researcher profile publications, institutions, and biographical records by ORCID iD.
- **Cross-category endpoints**: `pubchem_search`, `chembl_search`, `openalex_search`, `crossref_search`, `unpaywall_lookup`, `github_search`, `arxiv_search`, `semantic_scholar_search`, `core_search`.

### Category 2: Physical Sciences ⚛️
*Focus: Quantum physics, chemistry, condensed matter, and materials informatics.*
- **`arxiv_search`**: Real-time preprint discovery across quant-ph, cond-mat, physics, and math.
- **`openalex_search`**: Query 250M+ scholarly works with full citation graphs and institutional metadata.
- **`crossref_search`**: Query the Crossref metadata registry by DOI, author, title, or publication date.
- **`doe_pages_search`**: Discover research funded by the U.S. Department of Energy (DOE).
- **`chembl_search`**: Search 2M+ bioactive molecules, binding targets, assays, and IC50/Ki activities.
- **`pubchem_search`**: Chemical structure queries, IUPAC identifiers, SMILES resolution, and properties.
- **Cross-category endpoints**: `materials_project_search`, `semantic_scholar_search`, `unpaywall_lookup`, `github_search`, `core_search`.

### Category 3: Engineering & Computer Science 💻
*Focus: Machine learning, systems architecture, algorithms, and computational reproducibility.*
- **`semantic_scholar_search`**: High-precision academic paper search with citation velocity and paper graph traversal.
- **`dblp_search`**: Computer science bibliographic database for conferences and journals (NeurIPS, ICML, CVPR, IEEE).
- **`papers_with_code_search`**: Connect scientific papers to public code repositories, benchmarks, and SOTA leaderboards.
- **`github_search`**: Search open-source scientific research code, model weights, and benchmark suites.
- **`ieee_xplore_search`**: Index publications from IEEE journals, transactions, and technical standards.
- **Cross-category endpoints**: `arxiv_search` (cs.AI, cs.LG, cs.SE), `openalex_search`, `crossref_search`, `unpaywall_lookup`, `core_search`.

### Category 4: Earth & Environmental Sciences 🌍
*Focus: Biodiversity, climate records, satellite telemetry, and seismology.*
- **`gbif_search`**: Global Biodiversity Information Facility: search species occurrences and museum specimen records.
- **`nasa_search`**: Query NASA Open Data APIs for Earth observation telemetry, Landsat data, and astrophysics records.
- **`noaa_climate_search`**: Historical weather stations, temperature anomalies, and global precipitation datasets.
- **`usgs_earthquakes`**: Real-time USGS global earthquake telemetry, seismic depth, and fault rupture magnitudes.
- **`copernicus_data`**: Query European Space Agency Copernicus Sentinel atmospheric and land observation catalogs.
- **Cross-category endpoints**: `openalex_search`, `crossref_search`, `unpaywall_lookup`, `biorxiv_search`, `github_search`.

### Category 5: Interdisciplinary Science & Systematic Reviews 🔗
*Focus: PRISMA literature reviews, open access resolution, and meta-science synthesis.*
- **`core_search`**: Search full texts across global open access research repositories.
- **`unpaywall_lookup`**: Instant resolution of legal, open-access full-text PDF links for any DOI across 30M+ papers.
- **`doaj_search`**: Directory of Open Access Journals: discover peer-reviewed open access papers.
- **`zenodo_search`**: Search scientific data packages, software archives, and preprints hosted on CERN's Zenodo.
- **`figshare_search`**: Discover citable research figures, datasets, supplementary files, and posters.
- **`osf_preprints`**: Search preprints across Open Science Framework repositories.
- **Cross-category endpoints**: `arxiv_search`, `openalex_search`, `crossref_search`, `github_search`, `semantic_scholar_search`.

---

## 🔑 External API Keys Directory

StemClaw works out of the box with public unauthenticated rate limits. However, adding free personal API keys elevates your API quotas and speeds up deep investigations.

You can configure any of these keys in `.stemclaw/.env` or inside StemClaw by typing `/keys set <NAME>`:

| Environment Variable | Provider / Service | Free Portal | Rate Limit & Throughput Advantage |
|---|---|---|---|
| **`META_API_KEY`** *(Required)* | **Meta Model API** | [dev.meta.ai](https://dev.meta.ai) | Powers `muse-wonder` and `muse-spark` reasoning, planning, and synthesis |
| **`NCBI_API_KEY`** | **NCBI / PubMed** | [ncbi.nlm.nih.gov](https://www.ncbi.nlm.nih.gov/account/settings/) | Increases PubMed & GenBank throughput **3x** (from 3 req/s to 10 req/s) |
| **`SEMANTIC_SCHOLAR_API_KEY`** | **Semantic Scholar** | [semanticscholar.org](https://www.semanticscholar.org/product/api) | Raises rate limits **10x** and unlocks citation graph traversal |
| **`MATERIALS_PROJECT_API_KEY`** | **Materials Project** | [materialsproject.org](https://next-gen.materialsproject.org/api) | Unlocks crystal structures, bandgap DFT calculations, and phase diagrams |
| **`GITHUB_TOKEN`** | **GitHub** | [github.com/settings/tokens](https://github.com/settings/tokens) | Raises search API quota from **60 req/hr to 5,000 req/hr** |
| **`NASA_API_KEY`** | **NASA Open Data** | [api.nasa.gov](https://api.nasa.gov/) | Raises Earth observation & telemetry API quota from **30 to 1,000 req/hr** |
| **`NOAA_TOKEN`** | **NOAA Climate** | [ncdc.noaa.gov](https://www.ncdc.noaa.gov/cdo-web/token) | Provides authenticated access to global weather station historical sensor data |
| **`UNPAYWALL_EMAIL`** | **Unpaywall** | [unpaywall.org](https://unpaywall.org/products/api) | High-speed legal direct PDF resolution (any valid email) |
| **`CORE_API_KEY`** | **CORE API** | [core.ac.uk](https://core.ac.uk/services/api) | Full-text indexing across 200M+ open institutional repository papers |

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Collistus-Kibe/STEM-Claw.git
cd STEM-Claw
```

### 2. Set Up Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install StemClaw
```bash
pip install -e .
```

### 4. Launch StemClaw
```bash
python -m stemclaw
```

### 5. Smart Key Onboarding
On your first run, StemClaw will ask for your STEM loadout and prompt you for your Meta Model API key:
```text
Notice: Live Meta Model API key is not configured yet.
Do you have a Meta Model API key? [y/N]: y
Please paste your Meta Model API Key below (press Ctrl+V or Right-Click to paste):
API Key: ****************************************
✔ Live Meta Model API key saved to .stemclaw/.env and activated!
```
- **Real-Time Masking**: Any key you type or paste with `Ctrl+V` or Right-Click is masked immediately with asterisks (`*`).
- **Auto-Clipboard Detection**: If you already copied your key from [dev.meta.ai](https://dev.meta.ai), you can simply hit **Enter** and StemClaw will auto-detect it from your clipboard!
- **Safe Isolation**: Keys are saved locally to `.stemclaw/.env` (which is git-ignored and never committed or shared).

---

## 💬 Interactive REPL & Slash Commands

Inside the StemClaw terminal session, control your investigation using slash commands:

| Command | Action |
|---|---|
| **`/help`** | Display interactive commands reference and active tools |
| **`/deep [goal]`** | Launch autonomous, multi-epoch deep research on a scientific problem |
| **`/resume [task_id]`**| Resume an ongoing deep research investigation from checkpoint |
| **`/plan`** | Inspect the active research roadmap, current phase, and Evidence Locker |
| **`/keys`** | View authentication status for all external keys or configure one (`/keys set NAME`) |
| **`/skills [name]`** | List active domain skills or inspect procedural instructions |
| **`/loadout [1-5]`** | Hot-swap STEM category loadout mid-session without restarting |
| **`/model [name]`** | Switch active model (`muse-wonder`, `muse-spark`, `Llama-4-Maverick`) |
| **`/export [md\|tex\|bib]`**| Export conversation synthesis and citations to disk |
| **`/clear`** | Clear conversation history while preserving category and system prompt |
| **`/status`** | Display active session ID, loaded tools, and API key statuses |
| **`exit` / `quit`** | Close research session cleanly |

---

## 🔒 Security & Privacy

- **Local Secrets Isolation**: Credentials reside exclusively on your machine in `.stemclaw/.env`. They are never passed into model context and are strictly ignored by `.gitignore`.
- **Pre-Tool Execution Security Gate**: StemClaw's security hooks block directory traversal attacks and prevent the LLM from reading or modifying local `.env` files.
- **Reproducible Citations**: All retrieved papers are saved to a local SQLite database (`.stemclaw/cache.db`) so you can reproduce results offline without repeated API calls.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
