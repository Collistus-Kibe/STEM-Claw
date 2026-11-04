"""StemClaw CLI command entry and interactive category picker."""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.prompt import Prompt

from stemclaw import __version__
from stemclaw.agent.loop import AgentLoop
from stemclaw.config import get_settings
from stemclaw.model import get_model_adapter
from stemclaw.session.router import STEMCategory, get_loadout, parse_category
from stemclaw.session.state import SessionState
from stemclaw.keys import (
    check_meta_api_key_flow,
    EXTERNAL_KEYS_REGISTRY,
    save_key_to_env,
)
from stemclaw.session.hooks import get_hook_manager
from stemclaw.visuals.animations import install_visual_hooks
from stemclaw.visuals.banner import (
    print_banner,
    print_category_prompt,
    print_loadout_summary,
)

console = Console()


def check_and_prompt_keys(
    session: SessionState,
    interactive: bool = True,
) -> bool:
    """Intelligently check and prompt for live Meta API Key and surface category-specific optional keys.

    Returns:
        bool: True if live Meta API is ready to connect, False if key is missing/declined.
    """
    workspace_root = Path(session.workspace_root)
    ready = check_meta_api_key_flow(
        workspace_root=workspace_root,
        interactive=interactive,
    )
    if not ready:
        return False

    # Inform the user about relevant optional free keys for their active loadout
    settings = get_settings(reload=True)
    missing_for_category = []
    for key_name in session.suggested_keys:
        val = getattr(settings, key_name.lower(), None) or os.environ.get(key_name)
        if not val:
            missing_for_category.append(key_name)

    if missing_for_category and interactive and sys.stdin.isatty():
        console.print(
            f"[dim]Tip: Optional keys for this loadout: {', '.join(missing_for_category)} "
            f"(type /keys in session to configure)[/dim]"
        )

    return True


def initialize_environment(workspace_root: Path) -> None:
    """Ensure .stemclaw runtime directory and .env template exist."""
    stemclaw_dir = workspace_root / ".stemclaw"
    stemclaw_dir.mkdir(parents=True, exist_ok=True)

    env_path = stemclaw_dir / ".env"
    example_path = stemclaw_dir / ".env.example"

    # If .env does not exist, initialize from example template
    if not env_path.exists() and example_path.exists():
        env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")


def show_status(settings=None) -> int:
    """Display the active session status if present."""
    settings = settings or get_settings()
    if not SessionState.exists(settings.session_file):
        console.print("[yellow]No active StemClaw session found.[/yellow]")
        console.print("Run [bold cyan]python -m stemclaw[/bold cyan] to initialize a loadout.")
        return 0

    try:
        session = SessionState.load(settings.session_file)
        loadout = get_loadout(session.category)
        print_banner()
        print_loadout_summary(session, loadout)
        return 0
    except Exception as e:
        console.print(f"[bold red]Failed to read session:[/bold red] {e}")
        return 1


def prompt_user_for_category() -> STEMCategory:
    """Prompt the user with the exact question until a valid category is chosen."""
    prompt_str = "[bold cyan]Reply with STEM category [1-5][/bold cyan]"

    while True:
        try:
            choice = Prompt.ask(prompt_str, default="1")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]StemClaw launch aborted.[/dim]")
            sys.exit(0)

        cleaned = choice.strip()
        if cleaned.lower() in ("q", "quit", "exit"):
            console.print("[dim]Exiting StemClaw.[/dim]")
            sys.exit(0)

        parsed = parse_category(cleaned)
        if parsed is not None:
            return parsed

        console.print(
            f"[bold red]Invalid selection '{choice}'.[/bold red] "
            "Please enter a number between 1 and 5."
        )


def launch_m1(
    category_arg: Optional[str] = None,
    reset: bool = False,
    workspace_root: Optional[Path] = None,
) -> SessionState:
    """Execute the launch flow: banner -> 5 category boxes -> category pick -> ready confirmation."""
    settings = get_settings()
    root = workspace_root or settings.workspace_root
    initialize_environment(root)

    print_banner()

    # Determine category
    selected_category: Optional[STEMCategory] = None

    if category_arg:
        selected_category = parse_category(category_arg)
        if selected_category is None:
            console.print(
                f"[bold red]Unrecognized category argument: '{category_arg}'[/bold red]"
            )
            print_category_prompt()
            selected_category = prompt_user_for_category()
    else:
        # Display the 5 category boxes directly
        print_category_prompt()
        selected_category = prompt_user_for_category()

    # Create and persist new session state
    session = SessionState.create_for_category(selected_category, workspace_root=root)
    saved_path = session.save(root / ".stemclaw" / "session.json")
    loadout = get_loadout(selected_category)

    # Visual confirmation message
    console.print(
        f"\n[bold green]✔ Ready! Loaded [{loadout.code}: {loadout.display_name}][/bold green] "
        f"[dim]({len(loadout.endpoint_tools)} tools active, {len(loadout.default_skills)} skills primed)[/dim]\n"
    )
    return session


def main(argv: Optional[list] = None) -> int:
    """CLI entry point with argument parsing and agent loop initiation."""
    parser = argparse.ArgumentParser(
        prog="stemclaw",
        description="StemClaw: Skill-Driven STEM Research Agent for the Terminal IDE",
    )
    parser.add_argument(
        "-c",
        "--category",
        help="Reply with category: [1] Life Sciences [2] Physical Sciences [3] Engineering & CS [4] Earth & Environmental [5] Interdisciplinary",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--status",
        action="store_true",
        help="Print current session status and active tools",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset active session and prompt for category afresh",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in offline exploration mode",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="Run a single research turn non-interactively and exit",
        default=None,
    )
    parser.add_argument(
        "--deep",
        "--goal",
        dest="deep_goal",
        help="Launch long-horizon autonomous deep research on a scientific problem (minutes to hours)",
        default=None,
    )
    parser.add_argument(
        "--resume",
        help="Resume an ongoing deep research investigation from task ID",
        default=None,
    )
    parser.add_argument(
        "--max-epochs",
        type=int,
        default=15,
        help="Maximum epochs to run for deep research (default: 15)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Pacing delay in seconds between epochs (default: 0.0)",
    )
    parser.add_argument(
        "--no-repl",
        action="store_true",
        help="Initialize session and exit without launching REPL loop",
    )
    parser.add_argument(
        "--resume-last",
        action="store_true",
        help="Instantly resume previous in-flight chat session (used by /reload)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"stemclaw {__version__}",
    )

    args = parser.parse_args(argv)

    if args.status:
        return show_status()

    restored_msgs = []
    if args.resume_last:
        from stemclaw.agent.chat_store import get_chat_store
        snapshot = get_chat_store().load_last_snapshot()
        if snapshot:
            saved_cat = snapshot.get("category")
            restored_msgs = snapshot.get("messages", [])
            session = launch_m1(category_arg=saved_cat or args.category, reset=args.reset)
        else:
            session = launch_m1(category_arg=args.category, reset=args.reset)
    else:
        session = launch_m1(category_arg=args.category, reset=args.reset)

    if args.no_repl:
        return 0

    # Prompt for live Meta Model API key with smart [y/n] and masked input
    interactive = (not args.query and not args.no_repl and not args.resume_last)
    if not args.mock:
        check_and_prompt_keys(session, interactive=interactive)

    # Install scientific visual animation hooks for literature tool calls
    install_visual_hooks(get_hook_manager(), session.category, animate_in_tty=sys.stdout.isatty())

    adapter = get_model_adapter(force_mock=args.mock)
    loop = AgentLoop(session=session, adapter=adapter)

    if restored_msgs:
        loop.history.restore_messages(restored_msgs)
        console.print(f"[bold green]✔ In-place reload complete! Restored {len(restored_msgs)} messages from active chat.[/bold green]\n")

    # 1. Resume existing deep research task if requested
    if args.resume:
        from stemclaw.agent.deep_research import DeepResearchEngine
        from stemclaw.agent.planner import ResearchPlan
        try:
            plan = ResearchPlan.load(args.resume, workspace_root=session.workspace_root)
            plan.status = "active"
            engine = DeepResearchEngine(
                session=session,
                plan=plan,
                adapter=adapter,
                registry=loop.registry,
                max_epochs=plan.total_epochs_run + args.max_epochs,
                epoch_delay_seconds=args.delay,
            )
            report_path = engine.run()
            console.print(f"[bold green]✔ Investigation resumed and finished: {report_path}[/bold green]")
            return 0
        except Exception as e:
            console.print(f"[bold red]Failed to resume task '{args.resume}':[/bold red] {e}")
            return 1

    # 2. Launch new deep research task if requested
    if args.deep_goal:
        from stemclaw.agent.deep_research import DeepResearchEngine
        from stemclaw.agent.planner import ResearchPlan
        plan = ResearchPlan.create_for_goal(args.deep_goal, session.category)
        engine = DeepResearchEngine(
            session=session,
            plan=plan,
            adapter=adapter,
            registry=loop.registry,
            max_epochs=args.max_epochs,
            epoch_delay_seconds=args.delay,
        )
        report_path = engine.run()
        console.print(f"[bold green]✔ Deep research completed. Report: {report_path}[/bold green]")
        return 0

    if args.query:
        loop.run_turn(args.query)
        console.print(f"\n[bold green]Turn completed.[/bold green]")
        return 0

    loop.interactive_repl()
    return 0


if __name__ == "__main__":
    sys.exit(main())
