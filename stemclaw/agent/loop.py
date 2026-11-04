"""Interactive agent REPL loop coordinating model streaming and tool execution."""

import asyncio
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from stemclaw.agent.history import ConversationHistory
from stemclaw.agent.prompts import get_system_prompt
from stemclaw.keys import suggest_external_key_if_needed
from stemclaw.model import get_model_adapter
from stemclaw.model.adapter import ModelAdapter
from stemclaw.session.state import SessionState
from stemclaw.tools.base import ToolCall, ToolResult
from stemclaw.tools.registry import ToolRegistry, get_default_registry

console = Console()

TOOL_KEY_SUGGESTIONS = {
    "pubmed_search": ("NCBI_API_KEY", "Raises PubMed request throughput from 3 req/s to 10 req/s"),
    "ncbi_eutilities": ("NCBI_API_KEY", "Raises Entrez search throughput from 3 req/s to 10 req/s"),
    "semantic_scholar_search": ("SEMANTIC_SCHOLAR_API_KEY", "Raises rate limit 10x and unlocks citation graphs"),
    "materials_project_search": ("MATERIALS_PROJECT_API_KEY", "Unlocks crystal structures and DFT electronic calculations"),
    "github_repo_search": ("GITHUB_TOKEN", "Raises GitHub API rate limit from 60 req/hr to 5,000 req/hr"),
    "nasa_search": ("NASA_API_KEY", "Unlocks high-throughput Earth & astronomy sensor telemetry"),
    "noaa_climate_search": ("NOAA_TOKEN", "Unlocks global historical weather station climate data"),
}


class AgentLoop:
    """Core autonomous research agent REPL loop."""

    def __init__(
        self,
        session: SessionState,
        adapter: Optional[ModelAdapter] = None,
        registry: Optional[ToolRegistry] = None,
        verbose: bool = True,
    ) -> None:
        self.session = session
        self.adapter = adapter or get_model_adapter()
        self.registry = registry or get_default_registry(session.category)
        self.verbose = verbose

        system_prompt = get_system_prompt(session.category)
        self.history = ConversationHistory(system_prompt=system_prompt)

    def run_turn(
        self,
        user_input: str,
        verbose: Optional[bool] = None,
        max_tool_rounds: int = 25,
    ) -> str:
        """Execute an agent interaction turn with multi-step autonomous tool execution support."""
        is_verbose = self.verbose if verbose is None else verbose
        self.history.add_user_message(user_input)
        tools = self.registry.get_schemas()

        final_content = ""
        current_round = 0

        while current_round < max_tool_rounds:
            current_round += 1
            content_accumulator = []
            pending_tool_calls: list[ToolCall] = []

            # 1. Stream response or tool call from model
            if is_verbose:
                if current_round == 1:
                    console.print(f"\n[bold cyan]StemClaw ({self.adapter.model_name})[/bold cyan]: ", end="")
                else:
                    console.print(f"\n[bold cyan]StemClaw (Synthesis)[/bold cyan]: ", end="")

            for chunk in self.adapter.generate_stream(
                self.history.get_messages(), tools=tools
            ):
                if chunk.text_delta:
                    if is_verbose:
                        console.print(chunk.text_delta, end="")
                    content_accumulator.append(chunk.text_delta)
                if chunk.tool_calls:
                    pending_tool_calls.extend(chunk.tool_calls)

            if is_verbose:
                console.print()  # newline

            assistant_content = "".join(content_accumulator)

            # If no tools were requested, this is the final answer!
            if not pending_tool_calls:
                self.history.add_assistant_message(assistant_content)
                final_content = assistant_content
                break

            # If tools were requested, record assistant turn with tool calls
            self.history.add_assistant_message(
                assistant_content, tool_calls=pending_tool_calls
            )

            # 2. Execute requested tool calls locally
            for call in pending_tool_calls:
                # Proactively reason if an optional free external API key would boost this tool
                if call.name in TOOL_KEY_SUGGESTIONS:
                    k_name, k_reason = TOOL_KEY_SUGGESTIONS[call.name]
                    suggest_external_key_if_needed(
                        k_name,
                        reason=k_reason,
                        workspace_root=self.session.workspace_root,
                    )

                if is_verbose:
                    console.print(
                        Panel(
                            f"[bold yellow]Executing Tool:[/bold yellow] [bold cyan]{call.name}[/bold cyan]\n"
                            f"[dim]Arguments: {call.raw_arguments or call.arguments}[/dim]",
                            border_style="yellow",
                            padding=(0, 2),
                        )
                    )

                # Execute via registry
                result: ToolResult = self.registry.execute_call(call)

                if is_verbose:
                    border_color = "red" if result.is_error else "green"
                    output_text = result.output
                    if len(output_text) > 2000:
                        output_text = output_text[:2000] + f"\n... [truncated {len(result.output) - 2000} chars]"
                    console.print(
                        Panel(
                            f"[dim]{output_text}[/dim]",
                            title=f"[{border_color}]Tool Output: {result.name}[/{border_color}]",
                            border_style=border_color,
                            padding=(0, 2),
                        )
                    )

                # Append tool output to history
                self.history.add_tool_result(result)

        # Guaranteed Final Synthesis: If max rounds reached or final_content is empty, force synthesis
        if not final_content:
            if is_verbose:
                console.print("\n[bold cyan]StemClaw (Final Synthesis)[/bold cyan]: ", end="")
            forced_msgs = self.history.get_messages() + [
                {
                    "role": "user",
                    "content": "Synthesize your research findings now. Summarize the literature in clear structured paragraphs, state the conclusions, and confirm any files written.",
                }
            ]
            synth_accumulator = []
            for chunk in self.adapter.generate_stream(forced_msgs, tools=tools):
                if chunk.text_delta:
                    if is_verbose:
                        console.print(chunk.text_delta, end="")
                    synth_accumulator.append(chunk.text_delta)
                if chunk.tool_calls:
                    for tc in chunk.tool_calls:
                        res = self.registry.execute_call(tc)
                        self.history.add_tool_result(res)
            if is_verbose:
                console.print()
            final_content = "".join(synth_accumulator)
            if final_content:
                self.history.add_assistant_message(final_content)

        # Prominently display deliverables summary box
        from pathlib import Path
        root = Path(self.session.workspace_root)
        reports_dir = root / "reports"
        found_reports = []
        if reports_dir.exists():
            for p in sorted(reports_dir.glob("*.md")):
                found_reports.append(str(p.relative_to(root)))

        bib_file = root / "references.bib"
        has_bib = bib_file.exists()

        if is_verbose and (found_reports or has_bib):
            deliverables_text = "[bold green]✔ Research Deliverables Generated:[/bold green]\n"
            for r in found_reports:
                deliverables_text += f"\n  📄 [bold white]Report File:[/bold white] [bold cyan]{r}[/bold cyan]"
            if has_bib:
                deliverables_text += "\n  📚 [bold white]Bibliography:[/bold white] [bold cyan]references.bib[/bold cyan]"
            deliverables_text += "\n\n[dim]You can open and read the markdown report directly in your IDE or text editor.[/dim]"

            console.print(
                Panel(
                    deliverables_text,
                    title="[bold green]RESEARCH COMPLETE[/bold green]",
                    border_style="green",
                    padding=(0, 2),
                )
            )

        # Record turn in persistent chat store and snapshot for /reload
        try:
            from stemclaw.agent.chat_store import get_chat_store
            chat_store = get_chat_store()
            chat_store.record_turn(
                session_id=self.session.session_id,
                category=self.session.category_name,
                turn_index=self.history.count(),
                user_query=user_input,
                assistant_response=final_content,
            )
            cat_val = self.session.category.value if hasattr(self.session.category, "value") else str(self.session.category)
            chat_store.save_last_snapshot(
                session_id=self.session.session_id,
                category=cat_val,
                messages=self.history.get_messages(compact=False),
            )
            self.history.trim(max_turns=30)
        except Exception:
            pass

        return final_content

    def interactive_repl(self) -> None:
        """Run the interactive terminal REPL."""
        from stemclaw.agent.commands import handle_slash_command

        first_turn = (self.history.count() <= 1)
        while True:
            category_name = self.session.category_name
            code = self.session.category_code
            if first_turn:
                prompt_label = "[bold cyan]What would you like to research?[/bold cyan] > "
            else:
                prompt_label = f"[bold cyan]stemclaw [{code}:{category_name}][/bold cyan] > "

            try:
                user_input = Prompt.ask(prompt_label)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Ending research session.[/dim]")
                break

            cleaned = user_input.strip()
            if not cleaned:
                continue

            if cleaned.lower() in ("exit", "quit", "q", "/exit", "/quit", "/q"):
                console.print("[dim]Session closed.[/dim]")
                break

            # Check for direct category loadout switch (e.g. typing "2", "/2", "mode 2", "switch 2")
            if cleaned in ("1", "2", "3", "4", "5"):
                from stemclaw.agent.commands import _cmd_loadout
                _cmd_loadout(self, cleaned)
                continue

            parts = cleaned.split()
            if len(parts) == 2 and parts[0].lower() in ("mode", "switch", "loadout", "category") and parts[1] in ("1", "2", "3", "4", "5"):
                from stemclaw.agent.commands import _cmd_loadout
                _cmd_loadout(self, parts[1])
                continue

            # Check for slash command
            if cleaned.startswith("/"):
                handled = handle_slash_command(cleaned, self)
                if handled:
                    continue

            self.run_turn(cleaned)
            first_turn = False
