"""Interactive slash commands handler for the StemClaw REPL loop.

Provides Claude Code-style slash commands:
  /help      - Display available slash commands and loaded tools
  /skills    - List loaded skills and procedural instructions
  /loadout   - Switch category loadout dynamically mid-session
  /model     - Change live model (muse-wonder, muse-spark, Llama-4-Maverick)
  /export    - Export research session transcript to Markdown or LaTeX
  /clear     - Reset conversation history while preserving system prompt
  /status    - Display active session configuration and API keys
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from stemclaw.config import get_settings
from stemclaw.model import get_model_adapter
from stemclaw.session.router import (
    LOADOUT_CATALOG,
    STEMCategory,
    get_loadout,
    parse_category,
)
from stemclaw.session.state import SessionState
from stemclaw.skills.loader import get_skill_loader
from stemclaw.tools.registry import ToolRegistry, get_default_registry
from stemclaw.visuals.banner import print_loadout_summary

if TYPE_CHECKING:
    from stemclaw.agent.loop import AgentLoop

console = Console()


def handle_slash_command(command_line: str, loop: "AgentLoop") -> bool:
    """Check if input is a slash command and dispatch. Returns True if handled."""
    line = command_line.strip()
    if not line.startswith("/"):
        return False

    parts = line.split(maxsplit=2)
    cmd = parts[0].lower()
    arg1 = parts[1] if len(parts) > 1 else ""
    arg2 = parts[2] if len(parts) > 2 else ""

    if cmd in ("/help", "/?"):
        _cmd_help(loop)
        return True
    elif cmd == "/skills":
        _cmd_skills(loop, arg1)
        return True
    elif cmd in ("/loadout", "/category", "/mode", "/switch"):
        _cmd_loadout(loop, arg1)
        return True
    elif cmd in ("/1", "/2", "/3", "/4", "/5"):
        _cmd_loadout(loop, cmd[1:])
        return True
    elif cmd == "/model":
        _cmd_model(loop, arg1)
        return True
    elif cmd == "/export":
        _cmd_export(loop, arg1, arg2)
        return True
    elif cmd in ("/clear", "/new", "/reset"):
        _cmd_clear(loop)
        return True
    elif cmd == "/status":
        _cmd_status(loop)
        return True
    elif cmd in ("/deep", "/goal"):
        # Combine remaining parts for full research query
        goal_text = line[len(cmd):].strip()
        _cmd_deep(loop, goal_text)
        return True
    elif cmd == "/resume":
        _cmd_resume(loop, arg1)
        return True
    elif cmd == "/plan":
        _cmd_plan(loop)
        return True
    elif cmd in ("/keys", "/key", "/api-keys"):
        _cmd_keys(loop, arg1, arg2)
        return True
    elif cmd in ("/exit", "/quit", "/q"):
        console.print("[dim]Session closed.[/dim]")
        sys.exit(0)
    elif cmd in ("/download", "/get", "/save"):
        _cmd_download(loop, arg1)
        return True
    elif cmd in ("/chats", "/history"):
        _cmd_chats(loop, arg1, arg2)
        return True
    elif cmd in ("/memory", "/scratchpad"):
        _cmd_memory(loop, arg1, arg2)
        return True
    elif cmd in ("/reload", "/restart"):
        console.print("[bold green]✔ Saving chat state and reloading in-place...[/bold green]\n")
        try:
            from stemclaw.agent.chat_store import get_chat_store
            chat_store = get_chat_store()
            cat_val = loop.session.category.value if hasattr(loop.session.category, "value") else str(loop.session.category)
            chat_store.save_last_snapshot(
                session_id=loop.session.session_id,
                category=cat_val,
                messages=loop.history.get_messages(compact=False),
            )
        except Exception:
            pass
        import os
        os.execv(sys.executable, [sys.executable, "-m", "stemclaw", "--resume-last"])
    else:
        console.print(f"[yellow]Unknown command: '{cmd}'. Type [bold]/help[/bold] to see available commands.[/yellow]")
        return True


def _cmd_help(loop: "AgentLoop") -> None:
    """Print command menu and registered tools table."""
    table = Table(
        show_header=True,
        header_style="bold cyan on navy_blue",
        title="StemClaw Slash Commands",
        expand=True,
    )
    table.add_column("Command", style="bold yellow", width=22)
    table.add_column("Description", style="dim")

    table.add_row("/help", "Show this interactive commands reference")
    table.add_row("/deep [goal]", "Launch long-horizon deep autonomous research on a scientific problem")
    table.add_row("/resume [task_id]", "Resume an ongoing deep research investigation from checkpoint")
    table.add_row("/plan", "Inspect the roadmap and evidence locker of the active research task")
    table.add_row("/skills [name]", "List loaded domain skills or read full procedural guide for a skill")
    table.add_row("/loadout [1-5|name]", "Hot-swap active STEM category loadout mid-session")
    table.add_row("/model [name]", "Switch active live model (muse-wonder, muse-spark, Llama-4-Maverick)")
    table.add_row("/export [md|tex|bib] [file]", "Export session conversation and research report to disk")
    table.add_row("/new, /clear", "Start a new clean research chat while preserving loadout")
    table.add_row("/status", "Display session ID, active tools, repos, and API keys")
    table.add_row("/keys [set <NAME>]", "View or configure Meta & external free API keys (masked input)")
    table.add_row("/download [file]", "Copy latest research report & bibtex directly to laptop Downloads folder")
    table.add_row("/chats [load <id>]", "List past research sessions or resume previous chats")
    table.add_row("/memory [clear]", "Inspect persistent research scratchpad memory")
    table.add_row("/reload", "Hot-restart StemClaw in-place and restore active chat")
    table.add_row("/exit, exit, q", "Close the research session and return to shell")

    console.print(table)


def _cmd_skills(loop: "AgentLoop", skill_name_filter: str) -> None:
    """Display active skills and optionally display the activated body."""
    loader = get_skill_loader()
    category = loop.session.category
    skills = loader.load_skills_for_category(category)

    if skill_name_filter:
        target = skill_name_filter.strip().lower()
        matched = [s for s in skills if target in s.name.lower()]
        if not matched:
            console.print(f"[yellow]Skill '{skill_name_filter}' not found in active category.[/yellow]")
            return
        skill = matched[0]
        body = loader.get_skill_body(skill)
        console.print(Panel(
            body,
            title=f"[bold green]Skill Guide: {skill.name}[/bold green]",
            subtitle=f"[dim]Allowed Tools: {', '.join(skill.allowed_tools)}[/dim]",
            border_style="green",
        ))
        return

    table = Table(
        title=f"Loaded Skills ({len(skills)}/8 cap for {loop.session.category_name})",
        expand=True,
    )
    table.add_column("Priority", justify="center", width=8, style="cyan")
    table.add_column("Skill Name", style="bold green", width=28)
    table.add_column("Description", style="dim")
    table.add_column("Allowed Tools", style="magenta", width=26)

    for s in skills:
        tools_str = ", ".join(s.allowed_tools[:3]) + ("..." if len(s.allowed_tools) > 3 else "")
        table.add_row(str(s.priority), s.name, s.description, tools_str)

    console.print(table)
    console.print("[dim]Tip: Use '/skills <name>' or tool 'activate_skill' to inspect full procedures.[/dim]")


def _cmd_loadout(loop: "AgentLoop", category_str: str) -> None:
    """Hot-swap category loadout mid-session."""
    if not category_str:
        console.print("[yellow]Usage: /loadout [1-5 | category_name][/yellow]")
        console.print("  [1] Life Sciences  [2] Physical Sciences  [3] Engineering & CS")
        console.print("  [4] Earth & Environmental  [5] Interdisciplinary")
        return

    new_cat = parse_category(category_str)
    if new_cat is None:
        console.print(f"[bold red]Invalid category:[/bold red] '{category_str}'. Enter 1-5 or category name.")
        return

    if new_cat == loop.session.category:
        console.print(f"[cyan]Loadout already set to {loop.session.category_name}.[/cyan]")
        return

    # Update session state
    settings = get_settings()
    new_session = SessionState.create_for_category(new_cat, workspace_root=Path(loop.session.workspace_root))
    new_session.save(settings.session_file)

    # Refresh loop components
    loop.session = new_session
    loop.registry = ToolRegistry.create_for_category(new_cat)

    from stemclaw.agent.prompts import get_system_prompt
    loop.history.system_prompt = get_system_prompt(new_cat)

    # Update visual banner
    loadout = get_loadout(new_cat)
    print_loadout_summary(new_session, loadout)
    console.print(f"[bold green]✔ Hot-swapped loadout to [{loadout.code}] {loadout.display_name}[/bold green]\n")


def _cmd_model(loop: "AgentLoop", model_name: str) -> None:
    """Switch active live model dynamically."""
    if not model_name:
        console.print(f"Current live model: [bold cyan]{loop.adapter.model_name}[/bold cyan]")
        console.print("Usage: [bold]/model [muse-wonder-1.0 | muse-spark-1.3][/bold]")
        return

    from stemclaw.model.llama_client import LlamaModelAdapter
    settings = get_settings()
    api_key = settings.effective_api_key
    if not api_key:
        console.print("[bold red]Cannot switch model: META_API_KEY is not configured.[/bold red]")
        console.print("[dim]Use /keys set META_API_KEY to configure your live key.[/dim]")
        return

    loop.adapter = LlamaModelAdapter(
        api_key=api_key,
        model=model_name.strip(),
        fallback_model=settings.llama_fallback_model,
        base_url=settings.effective_api_base,
    )
    console.print(f"[green]✔ Switched active live model to [bold]{model_name.strip()}[/bold][/green]")


def _cmd_export(loop: "AgentLoop", export_format: str, filename: str) -> None:
    """Export conversation and research report."""
    fmt = (export_format or "md").lower()
    root = Path(loop.session.workspace_root)

    if fmt == "md":
        target = root / (filename or "RESEARCH_REPORT.md")
        lines = [
            f"# StemClaw Research Report: {loop.session.category_name}",
            f"**Session ID:** `{loop.session.session_id}` | **Date:** `{loop.session.started_at[:10]}`\n",
            "## Conversation & Synthesis Transcript\n",
        ]
        for msg in loop.history.get_messages():
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            if role == "System":
                continue
            if role == "Tool":
                name = msg.get("name", "Tool")
                lines.append(f"### [Tool: {name}]\n```\n{content}\n```\n")
            else:
                lines.append(f"### {role}\n{content}\n")

        target.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"[bold green]✔ Research report exported to [underline]{target}[/underline][/bold green]")

    elif fmt in ("bib", "bibtex"):
        target = root / (filename or "references.bib")
        # Read or check if references exist
        if target.exists():
            console.print(f"[cyan]References file exists at: [underline]{target}[/underline] ({target.stat().st_size} bytes)[/cyan]")
        else:
            target.write_text("% StemClaw Curated References\n\n", encoding="utf-8")
            console.print(f"[green]Initialized empty references file at: [underline]{target}[/underline][/green]")

    elif fmt in ("tex", "latex"):
        target = root / (filename or "research_paper.tex")
        tex_content = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{cite}
\usepackage{hyperref}

\title{StemClaw Research Synthesis: """ + loop.session.category_name + r"""}
\author{StemClaw Autonomous Agent}
\date{\today}

\begin{document}
\maketitle

\section{Introduction}
This document synthesizes findings gathered during the StemClaw research session.

\section{Literature Findings}
% Findings synthesized from session

\bibliographystyle{plain}
\bibliography{references}
\end{document}
"""
        target.write_text(tex_content, encoding="utf-8")
        console.print(f"[bold green]✔ LaTeX article draft exported to [underline]{target}[/underline][/bold green]")

    else:
        console.print(f"[yellow]Unknown format '{export_format}'. Supported formats: md, tex, bib[/yellow]")


def _cmd_clear(loop: "AgentLoop") -> None:
    """Clear conversation history messages."""
    import uuid
    loop.history.clear_messages()
    loop.session.session_id = str(uuid.uuid4())
    console.print("[bold green]✔ Started a new clean research chat! Previous chat saved to database.[/bold green]\n")


def _cmd_status(loop: "AgentLoop") -> None:
    """Display session status."""
    settings = get_settings()
    table = Table(title="StemClaw Session Status", box=None)
    table.add_column("Property", style="bold cyan", width=20)
    table.add_column("Value")

    table.add_row("Session ID", loop.session.session_id)
    table.add_row("Category", f"[{loop.session.category_code}] {loop.session.category_name}")
    table.add_row("Active Model", loop.adapter.model_name)
    table.add_row("Active Tools", f"{len(loop.session.active_tools)} tools loaded")
    table.add_row("Active Skills", f"{len(loop.session.active_skills)} skills (8 max)")
    table.add_row("Meta API Key", "[bold green]Configured (Live)[/bold green]" if settings.effective_api_key else "[bold red]Not Configured[/bold red]")
    table.add_row("Workspace", loop.session.workspace_root)

    console.print(Panel(table, border_style="cyan"))


_ACTIVE_RESEARCH_PLAN: Optional["ResearchPlan"] = None


def _cmd_deep(loop: "AgentLoop", goal: str) -> None:
    """Launch deep multi-epoch autonomous investigation."""
    global _ACTIVE_RESEARCH_PLAN
    from stemclaw.agent.deep_research import DeepResearchEngine
    from stemclaw.agent.planner import ResearchPlan

    clean_goal = goal.strip()
    if not clean_goal:
        from rich.prompt import Prompt
        clean_goal = Prompt.ask("[bold cyan]Enter deep research goal / question[/bold cyan]")
        if not clean_goal.strip():
            console.print("[yellow]Aborted: research goal cannot be empty.[/yellow]")
            return

    plan = ResearchPlan.create_for_goal(clean_goal, loop.session.category)
    _ACTIVE_RESEARCH_PLAN = plan

    engine = DeepResearchEngine(
        session=loop.session,
        plan=plan,
        adapter=loop.adapter,
        registry=loop.registry,
        max_epochs=10,
        epoch_delay_seconds=0.0,
    )
    engine.run()


def _cmd_resume(loop: "AgentLoop", task_id: str) -> None:
    """Resume an existing deep research investigation from disk checkpoint."""
    global _ACTIVE_RESEARCH_PLAN
    from stemclaw.agent.deep_research import DeepResearchEngine
    from stemclaw.agent.planner import ResearchPlan

    clean_id = task_id.strip()
    tasks_dir = Path(loop.session.workspace_root) / ".stemclaw" / "tasks"

    if not clean_id:
        if not tasks_dir.exists() or not list(tasks_dir.glob("*/plan.json")):
            console.print("[yellow]No saved deep research tasks found in .stemclaw/tasks/[/yellow]")
            return
        console.print("[bold cyan]Available Deep Research Tasks to Resume:[/bold cyan]")
        for p in tasks_dir.glob("*/plan.json"):
            try:
                loaded = ResearchPlan.load(str(p))
                console.print(f"  - `{loaded.task_id}`: {loaded.goal} (Phase: {loaded.current_phase_index+1}/{len(loaded.phases)}, Status: {loaded.status})")
            except Exception:
                pass
        return

    try:
        plan = ResearchPlan.load(clean_id, workspace_root=Path(loop.session.workspace_root))
        _ACTIVE_RESEARCH_PLAN = plan
        plan.status = "active"
        console.print(f"[green]✔ Resumed task '{plan.task_id}': '{plan.goal}'[/green]")

        engine = DeepResearchEngine(
            session=loop.session,
            plan=plan,
            adapter=loop.adapter,
            registry=loop.registry,
            max_epochs=plan.total_epochs_run + 10,
            epoch_delay_seconds=0.0,
        )
        engine.run()
    except Exception as e:
        console.print(f"[bold red]Failed to resume task '{clean_id}':[/bold red] {e}")


def _cmd_plan(loop: "AgentLoop") -> None:
    """Inspect active deep research plan roadmap."""
    global _ACTIVE_RESEARCH_PLAN
    from stemclaw.agent.planner import ResearchPlan

    plan = _ACTIVE_RESEARCH_PLAN
    if not plan:
        tasks_dir = Path(loop.session.workspace_root) / ".stemclaw" / "tasks"
        plans = sorted(tasks_dir.glob("*/plan.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if plans:
            try:
                plan = ResearchPlan.load(str(plans[0]))
                _ACTIVE_RESEARCH_PLAN = plan
            except Exception:
                pass

    if not plan:
        console.print("[yellow]No active research plan. Launch one using [bold]/deep <goal>[/bold].[/yellow]")
        return

    table = Table(title=f"Research Roadmap: {plan.task_id}", expand=True)
    table.add_column("Phase #", justify="center", width=8, style="cyan")
    table.add_column("Phase Title", style="bold", width=36)
    table.add_column("Status", width=14)
    table.add_column("Findings / Description", style="dim")

    for idx, p in enumerate(plan.phases):
        status_style = "green" if p.status.value == "completed" else ("yellow" if p.status.value == "in_progress" else "dim")
        table.add_row(
            str(idx + 1),
            p.title,
            f"[{status_style}]{p.status.value.upper()}[/{status_style}]",
            p.findings_summary or p.description,
        )

    console.print(table)
    console.print(f"[dim]Evidence Locker Items: {len(plan.evidence_locker)} | Total Epochs: {plan.total_epochs_run}[/dim]")


def _cmd_keys(loop: "AgentLoop", action: str = "", key_name: str = "") -> None:
    """View status or interactively configure external API keys with masked input."""
    from stemclaw.keys import (
        EXTERNAL_KEYS_REGISTRY,
        print_keys_status_table,
        read_masked_input,
        save_key_to_env,
    )

    clean_act = action.strip().lower()
    root = Path(loop.session.workspace_root)

    if not clean_act or clean_act == "status" or clean_act == "list":
        print_keys_status_table(root)
        return

    if clean_act in ("set", "add", "config", "configure"):
        target_key = key_name.strip().upper()
        if not target_key:
            console.print("[yellow]Usage: /keys set <KEY_NAME>[/yellow]")
            console.print(f"[dim]Supported keys: {', '.join(EXTERNAL_KEYS_REGISTRY.keys())}[/dim]")
            return

        if target_key not in EXTERNAL_KEYS_REGISTRY:
            console.print(f"[bold red]Unknown key:[/bold red] '{target_key}'")
            console.print(f"[dim]Supported keys: {', '.join(EXTERNAL_KEYS_REGISTRY.keys())}[/dim]")
            return

        info = EXTERNAL_KEYS_REGISTRY[target_key]
        console.print(f"[bold cyan]Configuring {target_key}[/bold cyan] ({info['name']})")
        console.print(f"[dim]Portal: {info['url']}[/dim]")
        console.print("[dim]Input will be masked with asterisks (*******):[/dim]")

        try:
            val = read_masked_input(f"Enter {target_key}: ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Aborted.[/dim]")
            return

        if val:
            save_key_to_env(target_key, val, workspace_root=root)
            get_settings(reload=True)
            console.print(f"[bold green]✔ Saved {target_key} to .stemclaw/.env and activated![/bold green]")
        else:
            console.print("[yellow]No key provided. Value unchanged.[/yellow]")
    else:
        console.print(f"[yellow]Unknown keys command '{action}'. Type /keys to see table or /keys set <NAME> to configure.[/yellow]")




def _cmd_chats(loop: "AgentLoop", subcmd: str, session_id: str) -> None:
    """Manage and inspect past conversation sessions."""
    from stemclaw.agent.chat_store import get_chat_store
    store = get_chat_store()
    action = (subcmd or "").lower().strip()

    if action == "load" and session_id:
        turns = store.get_session_turns(session_id)
        if not turns:
            console.print(f"[bold red]No past conversation found for session ID:[/bold red] '{session_id}'")
            return
        restored = []
        for t in turns:
            restored.append({"role": "user", "content": t["user_query"]})
            if t.get("assistant_response"):
                restored.append({"role": "assistant", "content": t["assistant_response"]})
        loop.history.restore_messages(restored)
        console.print(f"[bold green]✔ Restored {len(turns)} turns from session [{session_id}][/bold green]")
        return

    if action == "view" and session_id:
        turns = store.get_session_turns(session_id)
        if not turns:
            console.print(f"[bold red]No records found for session ID:[/bold red] '{session_id}'")
            return
        console.print(f"\n[bold cyan]=== Transcript for Session {session_id} ===[/bold cyan]\n")
        for t in turns:
            console.print(f"[bold yellow]User:[/bold yellow] {t['user_query']}")
            if t.get("assistant_response"):
                console.print(f"[bold green]StemClaw:[/bold green] {t['assistant_response']}\n")
        return

    sessions = store.list_sessions(limit=10)
    if not sessions:
        console.print("[dim]No past research chats recorded yet.[/dim]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan on navy_blue",
        title="Past StemClaw Research Sessions",
        expand=True,
    )
    table.add_column("Session ID", style="bold yellow", width=18)
    table.add_column("Category", style="cyan", width=18)
    table.add_column("First Query / Topic", style="white")
    table.add_column("Turns", justify="right", width=7)
    table.add_column("Last Active", style="dim", width=19)

    for s in sessions:
        table.add_row(
            s["session_id"][:16] + "...",
            s["category"],
            s["title"],
            str(s["turn_count"]),
            s["last_active_at"][:19].replace("T", " "),
        )

    console.print(table)
    console.print("[dim]Tip: Use '/chats load <session_id>' to resume any past chat session![/dim]\n")


def _cmd_memory(loop: "AgentLoop", subcmd: str, content: str = "") -> None:
    """Inspect and manage the persistent research scratchpad."""
    from stemclaw.agent.scratchpad import get_scratchpad
    pad = get_scratchpad()
    action = (subcmd or "").lower().strip()

    if action == "clear":
        pad.clear()
        console.print("[bold green]✔ Research scratchpad memory cleared.[/bold green]")
        return

    if action == "add" and content:
        pad.add_finding(content)
        console.print(f"[bold green]✔ Added to scratchpad memory:[/bold green] {content}")
        return

    console.print(
        Panel(
            pad.format_summary(),
            title="[bold cyan]Persistent Research Scratchpad Memory[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print("[dim]Tip: The agent automatically records findings here. Use '/memory clear' to reset.[/dim]\n")


def _cmd_download(loop: "AgentLoop", target_file: str = "") -> None:
    """Download research report(s) directly to the user's laptop Downloads folder."""
    import shutil
    from pathlib import Path

    downloads_dir = Path.home() / "Downloads"
    if not downloads_dir.exists():
        downloads_dir = Path.home() / "Desktop"

    workspace = Path(loop.session.workspace_root)
    reports_dir = workspace / "reports"

    candidates = []
    if target_file:
        p = workspace / target_file
        if not p.exists() and reports_dir.exists():
            p = reports_dir / target_file
        if p.exists():
            candidates.append(p)
        else:
            console.print(f"[bold red]File not found:[/bold red] '{target_file}' in workspace or reports/")
            return
    else:
        # Auto-pick newest markdown report in reports/
        if reports_dir.exists():
            md_files = sorted(reports_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
            if md_files:
                candidates.append(md_files[0])

        bib = workspace / "references.bib"
        if bib.exists():
            candidates.append(bib)

    if not candidates:
        console.print("[yellow]No research reports found in workspace to download yet.[/yellow]")
        console.print("[dim]Run a research prompt to generate a report, then use /download.[/dim]\n")
        return

    copied_files = []
    for src in candidates:
        dst = downloads_dir / src.name
        try:
            shutil.copy2(src, dst)
            copied_files.append((src.name, str(dst)))
        except Exception as e:
            console.print(f"[red]Failed to copy {src.name}: {e}[/red]")

    if copied_files:
        box_text = "[bold green]✔ Download Complete — Deliverables Copied to Laptop Downloads Folder:[/bold green]\n"
        for name, dst in copied_files:
            box_text += f"\n  📥 [bold white]{name}[/bold white] ➔ [bold cyan]{dst}[/bold cyan]"
        box_text += f"\n\n[dim]Original files remain safely preserved in: {reports_dir}[/dim]"

        console.print(
            Panel(
                box_text,
                title="[bold green]DOWNLOADED TO LAPTOP[/bold green]",
                border_style="green",
                padding=(0, 2),
            )
        )
