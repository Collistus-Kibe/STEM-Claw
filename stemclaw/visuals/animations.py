"""Scientific visual animations and terminal data flow effects."""

import sys
import time
from typing import Optional
from rich.console import Console
from rich.text import Text

from stemclaw.session.router import STEMCategory
from stemclaw.session.hooks import HookManager, get_hook_manager
from stemclaw.tools.base import ToolCall, ToolResult

console = Console(legacy_windows=False if sys.platform == "win32" else None)

CATEGORY_ACCENT_COLORS = {
    STEMCategory.LIFE_SCIENCES: "green",
    STEMCategory.PHYSICAL_SCIENCES: "bright_blue",
    STEMCategory.ENGINEERING_CS: "yellow",
    STEMCategory.EARTH_ENVIRONMENTAL: "cyan",
    STEMCategory.INTERDISCIPLINARY: "magenta",
}

LITERATURE_SEARCH_TOOLS = {
    "ncbi_esearch",
    "ncbi_efetch",
    "europe_pmc_search",
    "biorxiv_search",
    "uniprot_search",
    "orcid_lookup",
    "arxiv_search",
    "openalex_search",
    "crossref_search",
    "doe_pages_search",
    "chembl_search",
    "pubchem_search",
    "dblp_search",
    "semantic_scholar_search",
    "semantic_scholar_refs",
    "papers_with_code",
    "github_search",
    "ieee_xplore",
    "gbif_occurrences",
    "gbif_species",
    "nasa_media_search",
    "noaa_climate_data",
    "usgs_earthquakes",
    "copernicus_data",
    "core_search",
    "unpaywall_lookup",
    "doaj_search",
    "zenodo_search",
    "figshare_search",
    "osf_preprints",
}


def render_data_flowing_animation(
    tool_name: str,
    category: Optional[STEMCategory] = None,
    interactive_delay: bool = False,
) -> None:
    """Render a scientific 'data flowing' braille stream animation in the terminal."""
    cat = category or STEMCategory.LIFE_SCIENCES
    color = CATEGORY_ACCENT_COLORS.get(cat, "cyan")

    braille_frames = [
        "⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏",
        "⠇ ⠏ ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧",
        "⠼ ⠴ ⠦ ⠧ ⠇ ⠏ ⠋ ⠙ ⠹ ⠸",
    ]

    is_interactive = sys.stdout.isatty() and interactive_delay

    if is_interactive:
        for frame in braille_frames:
            text = Text()
            text.append(f"  {frame} ", style=f"bold {color}")
            text.append(f"[STREAMING DATA FLOW] ", style="dim")
            text.append(f"{tool_name} packet received", style=f"bold {color}")
            console.print(text, end="\r")
            time.sleep(0.08)
        console.print()
    else:
        # Clean single-line notification for non-interactive / CI / testing
        text = Text()
        text.append("  ⚡ [DATA PACKET] ", style=f"bold {color}")
        text.append(f"{tool_name} data stream ingested & synthesized", style="dim")
        console.print(text)


def install_visual_hooks(
    hook_mgr: Optional[HookManager] = None,
    category: Optional[STEMCategory] = None,
    animate_in_tty: bool = True,
) -> None:
    """Attach PostToolUse animation callback for all literature search endpoints."""
    mgr = hook_mgr or get_hook_manager()

    def post_tool_visual_callback(call: ToolCall, result: ToolResult) -> None:
        if call.name in LITERATURE_SEARCH_TOOLS and not result.is_error:
            render_data_flowing_animation(
                tool_name=call.name,
                category=category,
                interactive_delay=animate_in_tty,
            )

    mgr.register_post_tool_callback(post_tool_visual_callback)

