"""Scientific ASCII & Braille-inspired visual art for terminal display."""

from typing import Dict
from stemclaw.session.router import STEMCategory

STEMCLAW_ASCII_LOGO = r"""
  ____  _                     ____ _                 
 / ___|| |_ ___ _ __ ___     / ___| | __ ___      __ 
 \___ \| __/ _ \ '_ ` _ \   | |   | |/ _` \ \ /\ / / 
  ___) | ||  __/ | | | | |  | |___| | (_| |\ V  V /  
 |____/ \__\___|_| |_| |_|   \____|_|\__,_| \_/\_/   
             Autonomous STEM Research Agent
"""

STEMCLAW_LOGO = r"""
  ███████╗████████╗███████╗███╗   ███╗  ██████╗██╗      █████╗ ██╗    ██╗
  ██╔════╝╚══██╔══╝██╔════╝████╗ ████║ ██╔════╝██║     ██╔══██╗██║    ██║
  ███████╗   ██║   █████╗  ██╔████╔██║ ██║     ██║     ███████║██║ █╗ ██║
  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║ ██║     ██║     ██╔══██║██║███╗██║
  ███████║   ██║   ███████╗██║ ╚═╝ ██║ ╚██████╗███████╗██║  ██║╚███╔███╔╝
  ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ 
                   A Scientific Research Agent for the IDE
"""

ASCII_ROBOT_MASCOT = r"""
        ▲       ▲     
     ╭──┴───────┴──╮  
   c╭┤  ╭───────╮  ├╮ɔ
   ╰┤│  │ ◉   ◉ │  │├╯
    ││  │   ‿   │  ││ 
    ╰┤  ╰───────╯  ├╯ 
     ╰────┬───┬────╯  
       [ STEM-BOT ]   
"""

ASCII_ROBOT_MASCOT_SCANNING = r"""
        ▲       ▲     
     ╭──┴───────┴──╮  
   c╭┤  ╭───────╮  ├╮ɔ
   ╰┤│  │ ◎   ◎ │  │├╯
    ││  │  ═══  │  ││ 
    ╰┤  ╰───────╯  ├╯ 
     ╰────┬───┬────╯  
       [ STEM-BOT ]   
"""

ASCII_ROBOT_MASCOT_SUCCESS = r"""
        ▲       ▲     
     ╭──┴───────┴──╮  
   c╭┤  ╭───────╮  ├╮ɔ
   ╰┤│  │ ★   ★ │  │├╯
    ││  │   ▽   │  ││ 
    ╰┤  ╰───────╯  ├╯ 
     ╰────┬───┬────╯  
       [ STEM-BOT ]   
"""

ASCII_ROBOT_MONITOR = ASCII_ROBOT_MASCOT


ASCII_DNA_HELIX = r"""
               [1] LIFE SCIENCES: PROCEDURAL DNA DOUBLE HELIX
        .:::.                .:::.           
       :::::::.            .:::::::          A === T  [Adenine - Thymine]
      :::' ':::            :::' ':::         G === C  [Guanine - Cytosine]
     :::     :::          :::     :::        
    :::       :::        :::       :::       5' ───(P)───[Deoxyribose]─── 3'
    :::   -=- :::        :::   -=- :::           │     │     │     │
    :::  (A-T) :::======:::  (G-C) :::       3' ───[Ribose]───(P)─── 5'
     :::     :::          :::     :::        
      :::   :::            :::   :::         Transcriptome & Proteome
       ':::::'              ':::::'          Biochemical Kinematics
         :::                  :::            
      :::   :::            :::   :::         Active Tools: NCBI • bioRxiv
     :::     :::          :::     :::                      UniProt • Europe PMC
    :::  (C-G) :::======:::  (T-A) :::       
    :::   -=- :::        :::   -=- :::       
    :::       :::        :::       :::       
     :::     :::          :::     :::        
      ':::::::'            ':::::::'         
        ':::'                ':::'           
"""

ASCII_ATOM_LATTICE = r"""
            [2] PHYSICAL SCIENCES: QUANTUM ATOM & CRYSTAL LATTICE
                       .---.                       
                    .-'     '-.                    ψ(r,θ,φ) = R_nl(r) Y_lm(θ,φ)
                  .'     |     '.                  
                 /   .---+---.   \                 Ĥ |Ψ⟩ = E |Ψ⟩
                /   /    |    \   \                
               |   |  (  ●  )  |   |               Bravais Lattice: FCC / BCC
                \   \    |    /   /                Reciprocal k-space vector
                 \   '---+---'   /                 
                  '.     |     .'                  Active Tools: arXiv • OpenAlex
                    '-.     .-'                                 ChEMBL • Crossref
                       '---'                                    PubChem • DOE
             ┌─────────────┬─────────────┐         
             │  α = 5.43Å  │  FCC Si (d) │         
             └─────────────┴─────────────┘         
"""

ASCII_CIRCUIT_GEAR = r"""
            [3] ENGINEERING & CS: SILICON CORE & ALGORITHMIC GRAPH
          ┌───────────────────────────────────┐    
     ───► │  [ALU]  ◄──►  [LLM CO-PROCESSOR] │ ◄───  Complexity: O(N log N)
          └──────┬─────────────────────┬──────┘       Architecture: Transformer
                 │  01101001 01101110  │              Tensors: FP8 / BF16
          ┌──────┴─────────────────────┴──────┐       
          │  ● ───► ● ───► ●       (DAG Nodes)│       Throughput: 128k context
          │  │ ＼   │   ／ │                  │       
          │  ▼   ＼ ▼ ／   ▼                  │       Active Tools: DBLP • S2
          │  ● ───► ● ───► ●   [Distributed]  │                     PwC • GitHub
          └───────────────────────────────────┘                     IEEE Xplore
"""

ASCII_GLOBE_WAVE = r"""
          [4] EARTH & ENVIRONMENTAL: PLANETARY SPHERE & ECOSPHERE
                       .--------.                  
                    .-'  ____    '-.               Coordinate: WGS84
                  .'   .'  _ \_     '.             Remote Sensing: L1C / L2A
                 /   _/   /    \  _   \            Bioclimatic Envelope: RCP 4.5
                ;   /    ( Earth ) \   ;           
                |  |      \_____/   |  |           Carbon Flux: net ecosystem
                ;   \_    /     \  _/  ;           
                 \    \__/       \/   /            Active Tools: GBIF • NASA
                  '.    / \_     _  .'                           NOAA • USGS
                    '-.     \___/.-'                             Copernicus
                       '--------'                  
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      
               ≈≈ Atmospheric Wavefront ≈≈         
"""

ASCII_CONSTELLATION = r"""
            [5] INTERDISCIPLINARY: HYPERGRAPH & OPEN SCIENCE NEXUS
                    ( arXiv )                      
                        |                          Graph Density: ρ = 2|E|/(|V|(|V|-1))
                  ( Zenodo ) ── ( DOI )            Open Access Coverage: 84.2%
                   /        \     /                Cross-Domain Co-Citation Hub
           ( Crossref ) ──── ( Data )              
               │     \      /     │                Ontology: OpenAlex • Unpaywall
               │   ( OSF Preprints)│               
               │           │      │                Active Tools: CORE • Unpaywall
           ( Semantic ) ── ( Pub ) ── ( ORCID )                  DOAJ • Figshare
               \           /                                     Zenodo • OSF
                 ( Open Science )                  
"""

CATEGORY_ASCII_MAP: Dict[STEMCategory, str] = {
    STEMCategory.LIFE_SCIENCES: ASCII_DNA_HELIX,
    STEMCategory.PHYSICAL_SCIENCES: ASCII_ATOM_LATTICE,
    STEMCategory.ENGINEERING_CS: ASCII_CIRCUIT_GEAR,
    STEMCategory.EARTH_ENVIRONMENTAL: ASCII_GLOBE_WAVE,
    STEMCategory.INTERDISCIPLINARY: ASCII_CONSTELLATION,
}


def get_category_ascii(category: STEMCategory) -> str:
    """Retrieve the category's ASCII procedural visual."""
    return CATEGORY_ASCII_MAP.get(category, ASCII_DNA_HELIX)

