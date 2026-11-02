"""STEM Category Router and Loadout Definitions.

Maps each of the 5 STEM categories to its exact endpoint tools,
curated knowledge repositories, procedural skills (max 8), and visual theme.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class STEMCategory(str, Enum):
    LIFE_SCIENCES = "life_sciences"
    PHYSICAL_SCIENCES = "physical_sciences"
    ENGINEERING_CS = "engineering_cs"
    EARTH_ENVIRONMENTAL = "earth_environmental"
    INTERDISCIPLINARY = "interdisciplinary"


class RepoMetadata(BaseModel):
    name: str
    description: str
    topics: List[str] = Field(default_factory=list)


class CategoryLoadout(BaseModel):
    category: STEMCategory
    code: int
    display_name: str
    icon: str
    description: str
    visual_theme: str
    procedural_symbol: str
    endpoints: List[str]
    endpoint_tools: List[str]
    knowledge_repos: List[RepoMetadata]
    default_skills: List[str]
    suggested_keys: List[str]


# Curated Knowledge Repositories per category (8 each)
_LIFE_SCIENCES_REPOS = [
    RepoMetadata(
        name="danielecook/Awesome-Bioinformatics",
        description="Curated list of software: sequence analysis, variant calling, assembly, alignment",
        topics=["genomics", "bioinformatics", "pipeline"],
    ),
    RepoMetadata(
        name="araastat/awesome-computational-biology",
        description="Structural biology, multi-omics, CASP benchmarks, protein DBs (PDB, CATH, UniRef)",
        topics=["structural-biology", "proteins", "omics"],
    ),
    RepoMetadata(
        name="AdaptInfer/CompBioDatasetsForMachineLearning",
        description="Machine learning-ready datasets: TCGA, GEO, ENCODE, GTEx, single-cell atlases",
        topics=["datasets", "machine-learning", "single-cell"],
    ),
    RepoMetadata(
        name="cytodata/awesome-cytodata",
        description="Image-based profiling and spatial biology: Cell Painting, RxRx, microscopy",
        topics=["imaging", "spatial-biology", "cell-painting"],
    ),
    RepoMetadata(
        name="openmm/openmm",
        description="High-performance molecular dynamics simulation toolkit",
        topics=["simulation", "molecular-dynamics", "biophysics"],
    ),
    RepoMetadata(
        name="biopython/biopython",
        description="Standard computational molecular biology library in Python",
        topics=["python", "sequences", "pdb"],
    ),
    RepoMetadata(
        name="deepchem/deepchem",
        description="Deep learning platform for drug discovery, quantum chemistry, and biology",
        topics=["drug-discovery", "chemoinformatics", "deep-learning"],
    ),
    RepoMetadata(
        name="K-Dense-AI/scientific-agent-skills",
        description="Scientific agent skill recipes for bioinformatics, clinical, and genomics",
        topics=["agent-skills", "protocols", "workflows"],
    ),
]

_PHYSICAL_SCIENCES_REPOS = [
    RepoMetadata(
        name="tilde-lab/awesome-materials-informatics",
        description="Materials informatics, AFLOW, ASE, AiiDA, crystallography & structure toolkits",
        topics=["materials-science", "crystallography", "simulation"],
    ),
    RepoMetadata(
        name="hsiaoyi0504/awesome-cheminformatics",
        description="Cheminformatics directory: RDKit, Open Babel, virtual screening, docking",
        topics=["chemistry", "rdkit", "molecular-structures"],
    ),
    RepoMetadata(
        name="lmmentel/awesome-python-chemistry",
        description="Python tools for atomistic simulations, quantum chemistry, thermodynamics",
        topics=["computational-chemistry", "thermodynamics", "python"],
    ),
    RepoMetadata(
        name="blaiszik/awesome-matchem-datasets",
        description="Materials and chemistry ML datasets: Materials Project, AFLOW, Open Catalyst",
        topics=["datasets", "materials-project", "catalysis"],
    ),
    RepoMetadata(
        name="awesome-physics/awesome-neural-physics",
        description="Physics-informed neural networks (PINNs), differentiable physics simulators",
        topics=["pinns", "simulation", "neural-physics"],
    ),
    RepoMetadata(
        name="comp-physics/awesome-modeling-simulation",
        description="Numerical simulation methods, ODE/PDE solvers, classical/quantum dynamics",
        topics=["modeling", "simulation", "pde"],
    ),
    RepoMetadata(
        name="sherrylixuecheng/awesome-ai4chem",
        description="AI for chemistry: electronic structures, retrosynthesis, molecular dynamics",
        topics=["ai4chem", "retrosynthesis", "quantum-chemistry"],
    ),
    RepoMetadata(
        name="iris-hep/awesome-hep",
        description="High-energy physics data pipelines, event reconstruction, statistical fitting",
        topics=["particle-physics", "hep", "statistics"],
    ),
]

_ENGINEERING_CS_REPOS = [
    RepoMetadata(
        name="paperswithcode/paperswithcode-data",
        description="Curated ML benchmarks, evaluation leaderboards, task taxonomies, datasets",
        topics=["benchmarks", "leaderboards", "machine-learning"],
    ),
    RepoMetadata(
        name="josephmisiti/awesome-machine-learning",
        description="Comprehensive curated list of machine learning frameworks and algorithms",
        topics=["machine-learning", "deep-learning", "frameworks"],
    ),
    RepoMetadata(
        name="eugeneyan/applied-ml",
        description="Papers, architectures, and systems for machine learning applied in production",
        topics=["ml-systems", "production", "engineering"],
    ),
    RepoMetadata(
        name="dair-ai/ML-Papers-of-the-Week",
        description="Curated discoveries, trend digests, and breakthrough CS research papers",
        topics=["cs-papers", "deep-learning", "literature"],
    ),
    RepoMetadata(
        name="academic/awesome-datascience",
        description="Data science pipelines, visualization libraries, exploratory tools",
        topics=["data-science", "analytics", "visualization"],
    ),
    RepoMetadata(
        name="keon/awesome-nlp",
        description="Natural language processing models, benchmark datasets, tokenizers, linguistics",
        topics=["nlp", "transformers", "text-mining"],
    ),
    RepoMetadata(
        name="jbhuang0604/awesome-computer-vision",
        description="Computer vision literature, multimodal datasets, camera calibration, 3D vision",
        topics=["computer-vision", "multimodal", "image-processing"],
    ),
    RepoMetadata(
        name="K-Dense-AI/scientific-agent-skills",
        description="Agent skill protocols for code verification, algorithm analysis, benchmarking",
        topics=["agent-skills", "benchmarking", "code-analysis"],
    ),
]

_EARTH_ENVIRONMENTAL_REPOS = [
    RepoMetadata(
        name="rockita/Environmental_Intelligence",
        description="Earth system datasets: climate, hydrology, forestry, biodiversity, oceanography",
        topics=["climate-data", "earth-observation", "hydrology"],
    ),
    RepoMetadata(
        name="kartoza/awesome-geodata",
        description="Global geospatial data sources, vector/raster grids, climate portals, remote sensing",
        topics=["geospatial", "gis", "remote-sensing"],
    ),
    RepoMetadata(
        name="MasterCormac/awesome-environmental-science",
        description="Environmental science software, ecological models, vegetation indices, land cover",
        topics=["ecology", "vegetation-mapping", "environmental-science"],
    ),
    RepoMetadata(
        name="Awesome-Earth-Artificial-Intelligence/Awesome-Earth-Intelligence",
        description="AI applied to earth systems, disaster monitoring, biosphere tracking",
        topics=["earth-ai", "disaster-monitoring", "satellites"],
    ),
    RepoMetadata(
        name="gbif/pygbif",
        description="Official Python library for the Global Biodiversity Information Facility API",
        topics=["biodiversity", "species-occurrences", "taxonomy"],
    ),
    RepoMetadata(
        name="pangeo-data/pangeo",
        description="Cloud-native big-data geoscience stack: Xarray, Dask, Zarr, Copernicus",
        topics=["big-data", "xarray", "climate-modeling"],
    ),
    RepoMetadata(
        name="EarthyScience",
        description="Max Planck Institute for Biogeochemistry ecosystem models & micrometeorology",
        topics=["biogeochemistry", "ecosystems", "meteorology"],
    ),
    RepoMetadata(
        name="kbinani/climate-science-curated-list",
        description="Curated Python resources for atmospheric science, oceanography, hydrology",
        topics=["atmospheric-science", "oceanography", "python"],
    ),
]

_INTERDISCIPLINARY_REPOS = [
    RepoMetadata(
        name="JOSS-Reviewers/awesome-open-science",
        description="Open science tools, reproducible workflows, open data protocols, peer review",
        topics=["open-science", "reproducibility", "peer-review"],
    ),
    RepoMetadata(
        name="ContentMine/awesome-openaccess",
        description="Open access resources, institutional repositories, preprint registries, text mining",
        topics=["open-access", "preprints", "scholarly-communication"],
    ),
    RepoMetadata(
        name="shijuvar/awesome-open-data",
        description="High-value public and open-access datasets across all scientific branches",
        topics=["open-data", "public-records", "cross-domain"],
    ),
    RepoMetadata(
        name="allenai/s2orc",
        description="Semantic Scholar Open Research Corpus: 80M+ cross-domain paper full-texts",
        topics=["corpus", "citations", "cross-domain"],
    ),
    RepoMetadata(
        name="ourresearch/openalex-docs",
        description="Documentation and recipes for navigating the global OpenAlex scholarly graph",
        topics=["openalex", "knowledge-graph", "bibliometrics"],
    ),
    RepoMetadata(
        name="zenodo/zenodo",
        description="CERN's general-purpose open-access repository code and schema definitions",
        topics=["zenodo", "data-archiving", "doi"],
    ),
    RepoMetadata(
        name="OAI/OpenAPI-Specification",
        description="Standard machine-readable interface specifications for scientific web services",
        topics=["standards", "api-specs", "interoperability"],
    ),
    RepoMetadata(
        name="K-Dense-AI/scientific-agent-skills",
        description="Meta-scientific skills: systematic review, citation graphs, LaTeX formatting",
        topics=["systematic-review", "citation-network", "agent-skills"],
    ),
]


LOADOUT_CATALOG: Dict[STEMCategory, CategoryLoadout] = {
    STEMCategory.LIFE_SCIENCES: CategoryLoadout(
        category=STEMCategory.LIFE_SCIENCES,
        code=1,
        display_name="Life Sciences",
        icon="🧬",
        description="Molecular biology, genetics, bioinformatics, proteomics, and biomedicine",
        visual_theme="emerald",
        procedural_symbol="dna_helix",
        endpoints=[
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            "https://europepmc.org/rest/search",
            "https://api.biorxiv.org/details/biorxiv/",
            "https://rest.uniprot.org/uniprotkb/search",
            "https://pub.orcid.org/v3.0/",
        ],
        endpoint_tools=[
            "ncbi_esearch",
            "ncbi_efetch",
            "europe_pmc_search",
            "biorxiv_search",
            "uniprot_search",
            "orcid_lookup",
        ],
        knowledge_repos=_LIFE_SCIENCES_REPOS,
        default_skills=[
            "literature-search-pubmed",
            "protein-sequence-analysis",
            "bioinformatics-alignment",
            "gene-expression-profiling",
            "clinical-trials-lookup",
            "drug-target-interaction",
            "pathway-enrichment",
            "genomic-variants-annotation",
        ],
        suggested_keys=["NCBI_API_KEY"],
    ),
    STEMCategory.PHYSICAL_SCIENCES: CategoryLoadout(
        category=STEMCategory.PHYSICAL_SCIENCES,
        code=2,
        display_name="Physical Sciences",
        icon="⚛️",
        description="Physics, chemistry, materials science, astrophysics, and quantum systems",
        visual_theme="cobalt",
        procedural_symbol="atom_lattice",
        endpoints=[
            "https://export.arxiv.org/api/query",
            "https://api.openalex.org/works",
            "https://api.crossref.org/works",
            "https://osti.gov/pages/api/v1/records",
            "https://www.ebi.ac.uk/chembl/api/data/",
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/",
        ],
        endpoint_tools=[
            "arxiv_search",
            "openalex_search",
            "crossref_search",
            "doe_pages_search",
            "chembl_search",
            "pubchem_search",
        ],
        knowledge_repos=_PHYSICAL_SCIENCES_REPOS,
        default_skills=[
            "materials-property-lookup",
            "cheminformatics-rdkit",
            "spectroscopy-analysis",
            "crystal-structure-parsing",
            "quantum-chemistry-modeling",
            "thermodynamics-equations",
            "arxiv-physics-literature",
            "chemical-compound-screening",
        ],
        suggested_keys=["MATERIALS_PROJECT_API_KEY", "OPENALEX_MAILTO"],
    ),
    STEMCategory.ENGINEERING_CS: CategoryLoadout(
        category=STEMCategory.ENGINEERING_CS,
        code=3,
        display_name="Engineering & CS",
        icon="💻",
        description="Computer science, machine learning, systems architecture, robotics, and engineering",
        visual_theme="amber",
        procedural_symbol="circuit_gear",
        endpoints=[
            "https://dblp.org/search/publ/api",
            "https://api.semanticscholar.org/graph/v1/paper/search",
            "https://paperswithcode.com/api/v1/papers/",
            "https://api.github.com/search/repositories",
            "https://ieeexploreapi.ieee.org/api/v1/search/articles",
        ],
        endpoint_tools=[
            "dblp_search",
            "semantic_scholar_search",
            "semantic_scholar_refs",
            "papers_with_code",
            "github_search",
            "ieee_xplore",
        ],
        knowledge_repos=_ENGINEERING_CS_REPOS,
        default_skills=[
            "ml-benchmark-comparison",
            "algorithm-complexity-analysis",
            "dataset-explorer",
            "paper-review-rubric",
            "code-architecture-inspection",
            "systems-performance-profiling",
            "statistical-significance-test",
            "scientific-visualization",
        ],
        suggested_keys=["SEMANTIC_SCHOLAR_API_KEY", "GITHUB_TOKEN"],
    ),
    STEMCategory.EARTH_ENVIRONMENTAL: CategoryLoadout(
        category=STEMCategory.EARTH_ENVIRONMENTAL,
        code=4,
        display_name="Earth & Environmental",
        icon="🌍",
        description="Ecology, climate science, biodiversity, geology, hydrology, and earth observation",
        visual_theme="cyan",
        procedural_symbol="globe_wave",
        endpoints=[
            "https://api.gbif.org/v1/occurrence/search",
            "https://api.gbif.org/v1/species/search",
            "https://images.nasa.gov/search",
            "https://www.ncdc.noaa.gov/cdo-web/api/v2/",
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            "https://dataspace.copernicus.eu/odata/v1/",
        ],
        endpoint_tools=[
            "gbif_occurrences",
            "gbif_species",
            "nasa_media_search",
            "noaa_climate_data",
            "usgs_earthquakes",
            "copernicus_data",
        ],
        knowledge_repos=_EARTH_ENVIRONMENTAL_REPOS,
        default_skills=[
            "species-taxonomy-mapping",
            "climate-time-series-analysis",
            "satellite-remote-sensing",
            "ecological-niche-modeling",
            "biodiversity-hotspot-metrics",
            "geological-fault-survey",
            "water-quality-indices",
            "earthquake-event-analysis",
        ],
        suggested_keys=["NASA_API_KEY", "NOAA_TOKEN"],
    ),
    STEMCategory.INTERDISCIPLINARY: CategoryLoadout(
        category=STEMCategory.INTERDISCIPLINARY,
        code=5,
        display_name="Interdisciplinary",
        icon="🔗",
        description="Cross-domain synthesis, open science repositories, meta-science, and preprint graphs",
        visual_theme="amethyst",
        procedural_symbol="constellation_network",
        endpoints=[
            "https://api.core.ac.uk/v3/search/works",
            "https://api.unpaywall.org/v2/",
            "https://doaj.org/api/search/articles/",
            "https://zenodo.org/api/records",
            "https://api.figshare.com/v2/articles/search",
            "https://api.osf.io/v2/preprints/",
        ],
        endpoint_tools=[
            "core_search",
            "unpaywall_lookup",
            "doaj_search",
            "zenodo_search",
            "figshare_search",
            "osf_preprints",
        ],
        knowledge_repos=_INTERDISCIPLINARY_REPOS,
        default_skills=[
            "systematic-literature-review",
            "meta-analysis-synthesis",
            "open-access-fulltext-resolver",
            "citation-network-mapping",
            "research-data-management",
            "reproducibility-checklist",
            "experimental-design-evaluator",
            "academic-manuscript-formatter",
        ],
        suggested_keys=["CORE_API_KEY", "UNPAYWALL_EMAIL"],
    ),
}


def parse_category(val: str | int) -> Optional[STEMCategory]:
    """Parse user input into a valid STEMCategory.

    Supports:
      - Numbers: 1, 2, 3, 4, 5
      - Enum keys: 'life_sciences', 'physical_sciences', etc.
      - Partial or full names: 'life', 'biology', 'phys', 'cs', 'comp sci',
        'engineering', 'earth', 'climate', 'interdisciplinary', 'meta'
    """
    if isinstance(val, int):
        for loadout in LOADOUT_CATALOG.values():
            if loadout.code == val:
                return loadout.category
        return None

    cleaned = str(val).strip().lower()

    # Exact numeric string
    if cleaned in ("1", "[1]"):
        return STEMCategory.LIFE_SCIENCES
    if cleaned in ("2", "[2]"):
        return STEMCategory.PHYSICAL_SCIENCES
    if cleaned in ("3", "[3]"):
        return STEMCategory.ENGINEERING_CS
    if cleaned in ("4", "[4]"):
        return STEMCategory.EARTH_ENVIRONMENTAL
    if cleaned in ("5", "[5]"):
        return STEMCategory.INTERDISCIPLINARY

    # Exact enum values
    for cat in STEMCategory:
        if cleaned == cat.value:
            return cat

    # Fuzzy / keyword matching
    if any(k in cleaned for k in ("life", "bio", "med", "gene", "protein", "health")):
        return STEMCategory.LIFE_SCIENCES
    if any(k in cleaned for k in ("phys", "chem", "mater", "quant", "astro", "atom")):
        return STEMCategory.PHYSICAL_SCIENCES
    if any(k in cleaned for k in ("eng", "cs", "comp", "mach", "code", "softw", "robot")):
        return STEMCategory.ENGINEERING_CS
    if any(k in cleaned for k in ("earth", "env", "climat", "ecol", "geol", "ocean", "bio div")):
        return STEMCategory.EARTH_ENVIRONMENTAL
    if any(k in cleaned for k in ("inter", "cross", "open", "meta", "syn", "multi")):
        return STEMCategory.INTERDISCIPLINARY

    return None


def get_loadout(category: STEMCategory) -> CategoryLoadout:
    """Get the immutable loadout definition for a category."""
    return LOADOUT_CATALOG[category]

