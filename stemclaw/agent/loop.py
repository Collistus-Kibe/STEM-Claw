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
    ) -> str:
        """Execute a single agent interaction turn with tool execution support."""
        is_verbose = self.verbose if verbose is None else verbose
        self.history.add_user_message(user_input)
        tools = self.registry.get_schemas()

        content_accumulator = []
        pending_tool_calls: list[ToolCall] = []

        # 1. Stream primary response or tool call from model
        if is_verbose:
            console.print(f"\n[bold cyan]StemClaw ({self.adapter.model_name})[/bold cyan]: ", end="")
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

        # 2. If model requested tool calls, execute them locally
        if pending_tool_calls:
            # Record assistant turn that requested tool calls
            assistant_content = "".join(content_accumulator)
            self.history.add_assistant_message(
                assistant_content, tool_calls=pending_tool_calls
            )

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
                    console.print(
                        Panel(
                            f"[dim]{result.output}[/dim]",
                            title=f"[{border_color}]Tool Output: {result.name}[/{border_color}]",
                            border_style=border_color,
                            padding=(0, 2),
                        )
                    )

                # Append tool output to history
                self.history.add_tool_result(result)

            # 3. Model synthesizes final response incorporating tool results
            if is_verbose:
                console.print(f"[bold cyan]StemClaw (Synthesis)[/bold cyan]: ", end="")
            synthesis_accumulator = []
            for chunk in self.adapter.generate_stream(
                self.history.get_messages(), tools=tools
            ):
                if chunk.text_delta:
                    if is_verbose:
                        console.print(chunk.text_delta, end="")
                    synthesis_accumulator.append(chunk.text_delta)

            if is_verbose:
                console.print()
            final_content = "".join(synthesis_accumulator)
            self.history.add_assistant_message(final_content)
            return final_content

        # No tool calls; record standard assistant turn
        full_content = "".join(content_accumulator)
        self.history.add_assistant_message(full_content)
        return full_content

    def interactive_repl(self) -> None:
        """Run the interactive terminal REPL."""
        from stemclaw.agent.commands import handle_slash_command

        first_turn = True
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

            if cleaned.lower() in ("exit", "quit", "q"):
                console.print("[dim]Session closed.[/dim]")
                break

            # Check for slash command
            if cleaned.startswith("/"):
                handled = handle_slash_command(cleaned, self)
                if handled:
                    continue

            self.run_turn(cleaned)
            first_turn = False
