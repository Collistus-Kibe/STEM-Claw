"""Smart API key management, interactive masking, and external endpoint key reasoning."""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Set

# Ensure UTF-8 output on Windows consoles to prevent cp1252 charmap encoding errors
if sys.platform == "win32":
    os.system("")  # Enable VT100
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from stemclaw.config import get_settings

console = Console(safe_box=True)

# Registry of supported external free API keys that elevate search quality & throughput
EXTERNAL_KEYS_REGISTRY: Dict[str, Dict[str, str]] = {
    "META_API_KEY": {
        "name": "Meta Model API Key (Foundation)",
        "url": "https://dev.meta.ai",
        "category": "All Categories",
        "benefit": "Powers muse-wonder & muse-spark reasoning, synthesis, and deep research",
        "free": "Yes (Dev portal preview)",
    },
    "NCBI_API_KEY": {
        "name": "NCBI / PubMed Entrez Key",
        "url": "https://www.ncbi.nlm.nih.gov/account/settings/",
        "category": "Life Sciences",
        "benefit": "Increases PubMed / GenBank API throughput 3x (from 3 req/s to 10 req/s)",
        "free": "Yes (Free NCBI Account)",
    },
    "SEMANTIC_SCHOLAR_API_KEY": {
        "name": "Semantic Scholar API Key",
        "url": "https://www.semanticscholar.org/product/api",
        "category": "Engineering & CS",
        "benefit": "Boosts rate limits 10x and unlocks full citation graph traversal",
        "free": "Yes (Free Academic Tier)",
    },
    "MATERIALS_PROJECT_API_KEY": {
        "name": "Materials Project Key",
        "url": "https://next-gen.materialsproject.org/api",
        "category": "Physical Sciences",
        "benefit": "Enables crystal structures, bandgap DFT queries, and phase diagrams",
        "free": "Yes (Free Research Account)",
    },
    "GITHUB_TOKEN": {
        "name": "GitHub Personal Access Token",
        "url": "https://github.com/settings/tokens",
        "category": "Engineering & CS / All",
        "benefit": "Raises rate limit from 60 req/hr to 5,000 req/hr for code & benchmark discovery",
        "free": "Yes (Free GitHub Account)",
    },
    "NASA_API_KEY": {
        "name": "NASA Open Data Key",
        "url": "https://api.nasa.gov/",
        "category": "Earth & Environmental",
        "benefit": "Elevates astronomy & Earth observation satellite imagery API quotas",
        "free": "Yes (Free Instant Key)",
    },
    "NOAA_TOKEN": {
        "name": "NOAA Climate Data Token",
        "url": "https://www.ncdc.noaa.gov/cdo-web/token",
        "category": "Earth & Environmental",
        "benefit": "Provides access to global historical station and climate sensor datasets",
        "free": "Yes (Free NOAA Email Token)",
    },
    "UNPAYWALL_EMAIL": {
        "name": "Unpaywall Registered Email",
        "url": "https://unpaywall.org/products/api",
        "category": "Interdisciplinary / All",
        "benefit": "Unlocks high-speed Open Access direct PDF resolution across 30M+ papers",
        "free": "Yes (Any valid email)",
    },
    "CORE_API_KEY": {
        "name": "CORE API Key",
        "url": "https://core.ac.uk/services/api",
        "category": "Interdisciplinary",
        "benefit": "Full-text indexing and retrieval across global institutional repositories",
        "free": "Yes (Free Academic Tier)",
    },
}

# Cache of keys declined by user during active session so we don't nag
_DECLINED_KEYS_IN_SESSION: Set[str] = set()


def _get_windows_clipboard() -> str:
    """Safely read plain text from Windows clipboard if available."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        if not user32.OpenClipboard(None):
            return ""
        try:
            CF_UNICODETEXT = 13
            if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                return ""
            h_data = user32.GetClipboardData(CF_UNICODETEXT)
            if not h_data:
                return ""
            kernel32.GlobalLock.restype = ctypes.c_wchar_p
            ptr = kernel32.GlobalLock(h_data)
            text = str(ptr) if ptr else ""
            kernel32.GlobalUnlock(h_data)
            return text.strip()
        finally:
            user32.CloseClipboard()
    except Exception:
        return ""


def read_masked_input(prompt_text: str = "API Key: ") -> str:
    """Read API key with full native paste support (Ctrl+V, Right-Click, Shift+Insert).

    Immediately masks the input with asterisks (*******) upon submission.
    """
    sys.stdout.write(prompt_text)
    sys.stdout.flush()

    try:
        raw_input = input().strip()
    except (KeyboardInterrupt, EOFError):
        return ""

    # If user pressed Enter without typing/pasting, check if clipboard contains an API key
    if not raw_input and sys.platform == "win32":
        clip = _get_windows_clipboard()
        if clip and len(clip) >= 12:
            console.print("[dim](Auto-detected key from your clipboard!)[/dim]")
            raw_input = clip

    if raw_input:
        masked = "*" * len(raw_input)
        console.print(f"[bold green]✔ Key received: [cyan]{masked}[/cyan][/bold green]")

    return raw_input


def save_key_to_env(
    key_name: str, value: str, workspace_root: Optional[Path] = None
) -> None:
    """Save or update an API key in .stemclaw/.env and synchronize process environment."""
    root = workspace_root or Path.cwd()
    env_path = root / ".stemclaw" / ".env"
    env_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key_name}=") or line.strip().startswith(
            f"export {key_name}="
        ):
            new_lines.append(f"{key_name}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key_name}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ[key_name] = value


def check_meta_api_key_flow(
    workspace_root: Path,
    interactive: bool = True,
) -> bool:
    """Ensure a live Meta Model API key is present; prompt and save with masked input if missing.

    Returns:
        bool: True if live Meta Model API key is active, False if launch should abort.
    """
    settings = get_settings(reload=True)
    if settings.effective_api_key:
        console.print(
            f"[bold green]✔ Meta Model API: Connected[/bold green] "
            f"[dim]({settings.effective_model} live • dev.meta.ai)[/dim]"
        )
        return True

    if not interactive or not sys.stdin.isatty():
        console.print(
            "[bold red]Error: META_API_KEY is required for live reasoning and synthesis.[/bold red]\n"
            "[yellow]Please configure META_API_KEY in .stemclaw/.env or environment.[/yellow]"
        )
        return False

    console.print(
        "\n[bold yellow]Notice: Live Meta Model API key is not configured yet.[/bold yellow]"
    )

    try:
        choice = Prompt.ask(
            "[bold cyan]Do you have a Meta Model API key?[/bold cyan]",
            choices=["y", "n", "yes", "no"],
            default="y",
        )
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]StemClaw launch aborted.[/dim]")
        return False

    if choice.lower() in ("n", "no"):
        console.print(
            "\n[bold yellow]Running in Offline Exploration Mode.[/bold yellow]"
        )
        console.print(
            "[dim]Browse loadouts, inspect repositories, and format citations offline.[/dim]"
        )
        console.print(
            "[dim]To enable live Meta Model reasoning anytime: get a key at https://dev.meta.ai and type /keys set META_API_KEY.[/dim]\n"
        )
        return True

    # User answered YES: prompt with masked input
    console.print(
        "[bold cyan]Please paste your Meta Model API Key below (press Ctrl+V or Right-Click to paste):[/bold cyan]"
    )
    try:
        entered_key = read_masked_input("API Key: ")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]No key entered. Continuing in offline mode.[/dim]\n")
        return True

    if entered_key:
        save_key_to_env("META_API_KEY", entered_key, workspace_root=workspace_root)
        get_settings(reload=True)
        console.print(
            "[bold green]✔ Live Meta Model API key saved to .stemclaw/.env and activated![/bold green]\n"
        )
        return True
    else:
        console.print(
            "[yellow]No API key provided. Continuing in offline mode.[/yellow]\n"
        )
        return True


def suggest_external_key_if_needed(
    key_name: str,
    reason: str,
    workspace_root: Path,
) -> bool:
    """Proactively ask user if they have an external API key when agent reasons it would improve search.

    Returns:
        bool: True if key was provided and saved, False otherwise.
    """
    if key_name in _DECLINED_KEYS_IN_SESSION:
        return False

    settings = get_settings(reload=True)
    current_val = getattr(settings, key_name.lower(), None) or os.environ.get(key_name)
    if current_val:
        return True

    if not sys.stdin.isatty():
        return False

    info = EXTERNAL_KEYS_REGISTRY.get(key_name, {"name": key_name, "url": ""})
    display_name = info.get("name", key_name)
    url = info.get("url", "")

    console.print(
        Panel(
            f"[bold yellow]💡 Optimization Opportunity:[/bold yellow] {reason}\n"
            f"[dim]Endpoint: {display_name} ({url})[/dim]",
            border_style="yellow",
            padding=(0, 2),
        )
    )

    try:
        ans = Prompt.ask(
            f"[bold cyan]Do you have a free {key_name}?[/bold cyan]",
            choices=["y", "n", "yes", "no"],
            default="n",
        )
    except (KeyboardInterrupt, EOFError):
        _DECLINED_KEYS_IN_SESSION.add(key_name)
        return False

    if ans.lower() in ("y", "yes"):
        console.print(
            f"[bold cyan]Paste your {key_name} below (input will be masked):[/bold cyan]"
        )
        try:
            val = read_masked_input("Key: ")
        except (KeyboardInterrupt, EOFError):
            _DECLINED_KEYS_IN_SESSION.add(key_name)
            return False

        if val:
            save_key_to_env(key_name, val, workspace_root=workspace_root)
            get_settings(reload=True)
            console.print(
                f"[bold green]✔ Saved {key_name} to .stemclaw/.env! Using for upcoming calls.[/bold green]\n"
            )
            return True

    _DECLINED_KEYS_IN_SESSION.add(key_name)
    console.print(
        "[dim]Proceeding with public unauthenticated rate limits. No problem![/dim]\n"
    )
    return False


def print_keys_status_table(workspace_root: Optional[Path] = None) -> None:
    """Render a comprehensive Rich table of all supported keys and their live configuration status."""
    settings = get_settings(reload=True)
    table = Table(
        title="StemClaw External API Keys & Authentication Status",
        expand=True,
        header_style="bold cyan on navy_blue",
    )
    table.add_column("Environment Variable", style="bold yellow", width=26)
    table.add_column("Provider / Purpose", style="white", width=28)
    table.add_column("Status", width=14, justify="center")
    table.add_column("Throughput Advantage", style="dim")

    for env_var, meta in EXTERNAL_KEYS_REGISTRY.items():
        val = getattr(settings, env_var.lower(), None) or os.environ.get(env_var)
        if env_var == "META_API_KEY":
            val = val or settings.effective_api_key

        if val:
            status = "[bold green]✔ Configured[/bold green]"
        else:
            if env_var == "META_API_KEY":
                status = "[bold yellow]Missing (Core)[/bold yellow]"
            else:
                status = "[dim]Not Set (Public)[/dim]"

        table.add_row(
            env_var,
            meta["name"],
            status,
            meta["benefit"],
        )

    console.print(table)
    console.print(
        "[dim]To add any key, set it in .stemclaw/.env or type /keys configure <NAME> in the REPL.[/dim]\n"
    )

