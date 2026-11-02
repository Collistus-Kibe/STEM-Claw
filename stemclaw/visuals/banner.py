"""Terminal banner and summary cards rendered via Rich."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Safe reconfigure on Windows to support UTF-8 without crashing cp1252/cp437
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from stemclaw.session.router import CategoryLoadout, STEMCategory
from stemclaw.session.state import SessionState
from stemclaw.visuals.ascii_art import STEMCLAW_ASCII_LOGO, STEMCLAW_LOGO, get_category_ascii

console = Console(legacy_windows=False if sys.platform == "win32" else None)

# Theme color mappings
THEME_COLORS = {
    "emerald": "green",
    "cobalt": "bright_blue",
    "amber": "yellow",
    "cyan": "cyan",
    "amethyst": "magenta",
}


def print_banner(ascii_only: bool = False) -> None:
    """Print the primary StemClaw welcome banner and launch info."""
    encoding = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
    use_ascii = ascii_only or ("utf" not in encoding.lower())

    logo_content = STEMCLAW_ASCII_LOGO if use_ascii else STEMCLAW_LOGO
    lines = logo_content.strip("\n").split("\n")
    styled_logo = Text()
    for line in lines:
        if "Research Agent" in line or "Autonomous" in line:
            styled_logo.append(line.center(64) + "\n", style="bold bright_yellow")
        else:
            split_idx = 28 if use_ascii else 35
            if len(line) >= split_idx:
                styled_logo.append(line[:split_idx], style="bold cyan")
                styled_logo.append(line[split_idx:] + "\n", style="bold bright_magenta")
            else:
                styled_logo.append(line + "\n", style="bold cyan")

    panel = Panel(
        styled_logo,
        title="[bold bright_white on navy_blue] 🔬 STEMCLAW v0.1.0 [/bold bright_white on navy_blue]",
        subtitle="[bold cyan]Powered by Meta Model API[/bold cyan] [dim](muse-wonder / muse-spark) • Autonomous STEM Agent[/dim]",
        border_style="bright_blue",
        padding=(0, 2),
    )
    try:
        console.print(panel)
    except Exception:
        # Guaranteed ASCII fallback
        print("=" * 64)
        print("                 STEMCLAW v0.1.0")
        print("    Autonomous STEM Research Agent for the Terminal IDE")
        print("     Powered by Meta Model API (muse-wonder / muse-spark)")
        print("=" * 64)


def print_category_prompt() -> None:
    """Print the single category selection prompt."""
    table = Table(
        show_header=True,
        header_style="bold white on navy_blue",
        border_style="dim",
        expand=True,
    )
    table.add_column("Key", justify="center", style="bold cyan", width=6)
    table.add_column("Category", style="bold", width=24)
    table.add_column("Domain Focus", style="dim")

    table.add_row("[1]", "🧬 Life Sciences", "Genomics, Proteomics, NCBI/PubMed, Europe PMC, bioRxiv")
    table.add_row("[2]", "⚛️ Physical Sciences", "arXiv Physics, Materials Project, ChEMBL, PubChem, OpenAlex")
    table.add_row("[3]", "💻 Engineering & CS", "Semantic Scholar, DBLP, Papers With Code, GitHub, IEEE")
    table.add_row("[4]", "🌍 Earth & Environmental", "GBIF Biodiversity, NASA Open Data, NOAA Climate, USGS")
    table.add_row("[5]", "🔗 Interdisciplinary", "CORE API, Unpaywall, DOAJ, Zenodo, Figshare, OSF")

    panel = Panel(
        table,
        title="[bold yellow]Loadout Selection Required[/bold yellow]",
        subtitle="[bold white]Reply with STEM category: [1] Life Sciences [2] Physical Sciences [3] Engineering & CS [4] Earth & Environmental [5] Interdisciplinary[/bold white]",
        border_style="yellow",
        padding=(1, 1),
    )
    console.print(panel)


def print_loadout_summary(session: SessionState, loadout: CategoryLoadout) -> None:
    """Print the post-selection visual confirmation and loaded endpoints."""
    theme_color = THEME_COLORS.get(loadout.visual_theme, "cyan")

    # 1. Print the scientific procedural ASCII art
    ascii_art = get_category_ascii(loadout.category)
    console.print(Panel(
        Text(ascii_art, style=f"bold {theme_color}"),
        title=f"[bold {theme_color}]{loadout.icon} {loadout.display_name} Active Visual[/bold {theme_color}]",
        subtitle=f"[dim]Theme: {loadout.visual_theme} • Symbol: {loadout.procedural_symbol}[/dim]",
        border_style=theme_color,
    ))

    # 2. Print loadout components table
    summary_table = Table(show_header=False, box=None, padding=(0, 1))
    summary_table.add_column("Component", style="bold white", width=22)
    summary_table.add_column("Details", style="dim")

    summary_table.add_row(
        "Session ID:",
        f"[bold {theme_color}]{session.session_id}[/bold {theme_color}]",
    )
    summary_table.add_row(
        "Loadout:",
        f"[bold]{loadout.icon} [{loadout.code}] {loadout.display_name}[/bold] — {loadout.description}",
    )
    summary_table.add_row(
        "Session State File:",
        f"[green]{session.workspace_root}/.stemclaw/session.json[/green]",
    )
    summary_table.add_row(
        f"Active Tools ({len(session.active_tools)}):",
        ", ".join([f"[cyan]{t}[/cyan]" for t in session.active_tools]),
    )
    summary_table.add_row(
        f"Knowledge Repos ({len(session.active_repos)}):",
        ", ".join([f"[magenta]{r}[/magenta]" for r in session.active_repos[:5]])
        + (f" + {len(session.active_repos)-5} more" if len(session.active_repos) > 5 else ""),
    )
    summary_table.add_row(
        f"Active Skills ({len(session.active_skills)} max 8):",
        ", ".join([f"[yellow]{s}[/yellow]" for s in session.active_skills]),
    )

    if session.suggested_keys:
        summary_table.add_row(
            "Suggested Keys:",
            ", ".join([f"[italic red]{k}[/italic red]" for k in session.suggested_keys])
            + " (optional, configure in [bold].stemclaw/.env[/bold])",
        )

    summary_panel = Panel(
        summary_table,
        title=f"[bold {theme_color}]Loadout Initialized — Session Primed[/bold {theme_color}]",
        border_style=theme_color,
        padding=(1, 2),
    )
    console.print(summary_panel)
