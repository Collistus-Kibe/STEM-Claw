# StemClaw 🦀🔬

**A Skill-Driven STEM Research Agent for the Terminal IDE**

StemClaw is a Claude Code–style autonomous research agent that runs inside your IDE terminal. Powered by the **Meta Model API** (`dev.meta.ai` / `api.meta.ai/v1`, targeting `muse-wonder` and `muse-spark`), it uses a **loadout architecture**: choose one of five STEM categories at launch, and StemClaw loads *only* that category's endpoint tools, curated knowledge repositories, and procedural skills.

---

## ⚡ Architecture & Features

- **🎯 5 STEM Category Loadouts**: Launch-time specialization. Selecting a domain primes the agent with exact tools and knowledge, keeping context compact and focused.
- **🤖 Meta Model API**: Connects to hosted Meta model endpoints (`https://api.meta.ai/v1` or `https://api.llama.com/v1`) with:
  - `muse-wonder` (Default frontier agentic model: 1M context, planning, subagent delegation, coding)
  - `muse-wonder-full` (SOTA developer model)
  - `muse-spark` (Fast, lightweight multimodal reasoning)
  - Offline testing mode via `MockModelAdapter`.
- **💻 Claude Code-Style Slash Commands**:
  - `/help`: interactive command reference and registered tool table
  - `/skills [name]`: list loaded skills or view procedural guides
  - `/loadout [1-5|name]`: hot-swap category loadouts mid-session without restarting
  - `/model [name]`: toggle between `muse-wonder`, `muse-spark`, or `mock` dynamically
  - `/export [md|tex|bib] [file]`: compile conversation and synthesis into markdown notes, a LaTeX `.tex` draft, or BibTeX entries
  - `/clear`: clear history while preserving category and system prompt
  - `/status`: check session state, loaded endpoints, and API key statuses
- **📚 Citation Manager & BibTeX Exporter**:
  - `export_bibtex`: automatically formats and appends standardized citations to `references.bib` with deterministic citekeys (`vaswani2017attention`).
  - `format_citation`: instantly formats papers in APA 7th, IEEE, Nature, or Chicago style.
- **🔬 Scientific Python Runner & Dataset Inspector**:
  - `python_eval`: sandboxed mathematical formulas, statistical tests (mean, stdev, p-values), and unit conversions with pre-imported scientific modules.
  - `dataset_inspect`: profile tabular datasets (`.csv`, `.tsv`), JSON payloads, and genomic sequence files (`.fasta`, `.fa`) with GC content calculation.
- **💾 Local SQLite Literature Cache & Research Memory**:
  - `.stemclaw/cache.db`: caches retrieved papers, abstracts, and DOIs locally.
  - `search_local_papers`: instant, offline search across past discoveries without consuming API rate limits.
- **🛡️ Hook Security Gates & Secret Isolation**:
  - `PreToolUse`: Validates workspace boundaries to prevent traversal attacks, prohibits model writes to `.stemclaw/.env`, and injects API credentials on the fly without leaking them into model context.
  - `PostToolUse`: Fires real-time braille/ASCII "data flowing" terminal animations whenever scientific literature endpoints return data.

---

## 🔬 STEM Categories & Loadouts

| # | Category | Visual Theme & Art | Endpoints & Tools | Knowledge Repositories |
|---|---|---|---|---|
| **[1]** | **Life Sciences 🧬** | Emerald (DNA Double Helix) | NCBI E-Search, NCBI E-Fetch, Europe PMC, bioRxiv, UniProt, ORCID | Awesome-Bioinformatics, Awesome-Computational-Biology, CompBioDatasets, DeepChem, BioPython |
| **[2]** | **Physical Sciences ⚛️** | Cobalt (Atom & Crystal Lattice) | arXiv, OpenAlex, Crossref, DOE PAGES, ChEMBL, PubChem | Awesome-Materials-Informatics, Awesome-Cheminformatics, Awesome-Neural-Physics, AFLOW |
| **[3]** | **Engineering & CS 💻** | Amber (Silicon Circuit & Graph) | DBLP, Semantic Scholar (Search & Refs), Papers with Code, GitHub Search, IEEE Xplore | Papers with Code Data, Applied ML, ML Papers of the Week, Awesome Data Science |
| **[4]** | **Earth & Environmental 🌍** | Cyan (Planetary Sphere & Waves) | GBIF (Occurrences & Species), NASA Media, NOAA Climate, USGS Earthquakes, Copernicus | Environmental Intelligence, Awesome GeoData, PyGBIF, Pangeo |
| **[5]** | **Interdisciplinary 🔗** | Amethyst (Constellation Network) | CORE API, Unpaywall, DOAJ, Zenodo, Figshare, OSF Preprints | Awesome Open Science, Awesome Open Data, Semantic Scholar S2ORC, Zenodo |

---

## 🛠️ Built-in Agent Tools (Always Active)

- `file_read`: Inspect local workspace research notes, code, and datasets.
- `file_write`: Safely save synthesis reports, literature notes, and scripts.
- `list_directory`: Discover project files and research structures.
- `suggest_repo`: Look up domain-specific curated GitHub repositories.
- `activate_skill`: Lazily activate and read full procedural guidelines for a specialized skill.
- `export_bibtex`: Append formatted citations into `references.bib`.
- `format_citation`: Generate APA, IEEE, Nature, or Chicago citations.
- `python_eval`: Compute formulas, run statistical analysis, or calculate metrics.
- `dataset_inspect`: Profile CSV/TSV dimensions, null counts, or parse FASTA sequence lengths and GC content.
- `search_local_papers`: Search previous literature findings in `.stemclaw/cache.db`.
- `echo_tool`: Diagnostic pipeline verification ping.

---

## 🚀 Quickstart Guide

### 1. Installation & Setup
```bash
python -m pip install -e .
cp .stemclaw/.env.example .stemclaw/.env
```

### 2. Configure Meta Model API Key
In `.stemclaw/.env`:
```ini
META_API_KEY=your_key_from_dev_meta_ai
META_MODEL=muse-wonder
```

### 3. Launch StemClaw
Start the interactive terminal session:
```bash
python -m stemclaw
```
StemClaw prints the banner, visual theme, and asks for your category:
```text
Reply with STEM category: [1] Life Sciences [2] Physical Sciences [3] Engineering & CS [4] Earth & Environmental [5] Interdisciplinary
```

### 4. Interactive REPL Slash Commands
Inside the terminal session, use slash commands:
```text
stemclaw [1:Life Sciences] > /help
stemclaw [1:Life Sciences] > /skills
stemclaw [1:Life Sciences] > /loadout 2
stemclaw [2:Physical Sciences] > /model muse-spark
stemclaw [2:Physical Sciences] > /export md my_notes.md
stemclaw [2:Physical Sciences] > /status
```

---

## 🧪 Testing & Verification

Run the full test suite (88 unit and integration tests):
```bash
python -m pytest tests -v
```
All 88 tests pass with full mock coverage for all live endpoints, skill loaders, hook managers, and the end-to-end research loop.
