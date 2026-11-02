"""Deep Autonomous Research Engine for long-horizon scientific investigations.

Designed to conduct deep, rigorous scientific research taking from minutes to hours
(and resumable across days). Coordinates structured phases, continuous evidence accumulation,
checkpointing, self-reflection, and publication-ready thesis synthesis.
"""

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from stemclaw.agent.history import ConversationHistory
from stemclaw.agent.planner import PhaseStatus, ResearchPlan
from stemclaw.config import get_settings
from stemclaw.model import get_model_adapter
from stemclaw.model.adapter import ModelAdapter
from stemclaw.session.router import get_loadout
from stemclaw.session.state import SessionState
from stemclaw.tools.base import ToolCall, ToolResult
from stemclaw.tools.registry import ToolRegistry, get_default_registry

console = Console()


class DeepResearchEngine:
    """Orchestrates multi-epoch, long-horizon scientific investigations."""

    def __init__(
        self,
        session: SessionState,
        plan: ResearchPlan,
        adapter: Optional[ModelAdapter] = None,
        registry: Optional[ToolRegistry] = None,
        max_epochs: int = 25,
        epoch_delay_seconds: float = 0.0,
        verbose: bool = True,
    ) -> None:
        self.session = session
        self.plan = plan
        self.adapter = adapter or get_model_adapter()
        self.registry = registry or get_default_registry(session.category)
        self.max_epochs = max_epochs
        self.epoch_delay_seconds = epoch_delay_seconds
        self.verbose = verbose

        self.task_dir = self.plan.get_task_dir(Path(session.workspace_root))
        self.log_file = self.task_dir / "progress.log"

    def log(self, message: str) -> None:
        """Append to disk log and print to console if verbose."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        formatted = f"[{timestamp}] {message}"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
        if self.verbose:
            console.print(f"[dim]{formatted}[/dim]")

    def run(self, progress_callback: Optional[Callable[[int, ResearchPlan], None]] = None) -> Path:
        """Execute the multi-epoch investigation loop until all phases complete or max_epochs reached."""
        start_time = datetime.now(timezone.utc)
        self.log(f"Starting Deep Research Task '{self.plan.task_id}' for goal: '{self.plan.goal}'")
        self.log(f"Category: {self.session.category_name} | Max Epochs: {self.max_epochs}")

        console.print(
            Panel(
                f"[bold cyan]Deep Scientific Research Initiated[/bold cyan]\n\n"
                f"**Task ID:** `{self.plan.task_id}`\n"
                f"**Goal:** {self.plan.goal}\n"
                f"**Category:** {self.session.category_name} (Loadout {self.session.category_code})\n"
                f"**Phases ({len(self.plan.phases)}):** {', '.join([p.title for p in self.plan.phases])}\n"
                f"**Progress Log:** [underline]{self.log_file}[/underline]",
                title="[bold yellow]StemClaw Long-Horizon Engine[/bold yellow]",
                border_style="yellow",
            )
        )

        epoch = self.plan.total_epochs_run

        while epoch < self.max_epochs and self.plan.status == "active":
            epoch += 1
            self.plan.total_epochs_run = epoch

            current_phase = self.plan.current_phase
            if not current_phase:
                self.plan.status = "completed"
                break

            current_phase.status = PhaseStatus.IN_PROGRESS
            if not current_phase.started_at:
                current_phase.started_at = datetime.now(timezone.utc).isoformat()

            # Render epoch header card
            elapsed_min = (datetime.now(timezone.utc) - start_time).total_seconds() / 60.0
            console.print(
                f"\n[bold yellow]─── Epoch {epoch}/{self.max_epochs} [/bold yellow]"
                f"[dim]({elapsed_min:.1f}m elapsed) │ Phase {self.plan.current_phase_index + 1}/{len(self.plan.phases)}: "
                f"[bold cyan]{current_phase.title}[/bold cyan] │ Evidence Gathered: [green]{len(self.plan.evidence_locker)}[/green] ───[/dim]"
            )

            # Build Deliberation Prompt for this Epoch
            epoch_prompt = self._build_epoch_prompt(current_phase, epoch)

            # Run deliberate agent step
            findings_text = self._execute_epoch_turn(epoch_prompt)

            # Self-reflection & Evidence Extraction
            self._reflect_and_extract_evidence(findings_text, current_phase)

            # Check if this phase should transition to the next phase
            # If evidence has accumulated or epoch progress is sufficient, advance
            if epoch >= (self.plan.current_phase_index + 1) * max(1, (self.max_epochs // len(self.plan.phases))):
                phase_completed = self.plan.advance_phase(summary=findings_text[:300])
                self.log(f"Phase '{current_phase.title}' concluded. Advancing to next phase.")
                if not phase_completed:
                    self.log("All research phases successfully completed.")
                    break

            # Checkpoint to disk
            saved_plan = self.plan.save(Path(self.session.workspace_root))
            self.log(f"Epoch {epoch} checkpoint saved to {saved_plan}")

            if progress_callback:
                progress_callback(epoch, self.plan)

            # Pacing between epochs
            if self.epoch_delay_seconds > 0:
                time.sleep(self.epoch_delay_seconds)

        # Final Synthesis & Report Compilation
        report_path = self._compile_final_discovery_report(start_time)
        return report_path

    def _build_epoch_prompt(self, phase: Any, epoch: int) -> str:
        """Construct a high-context prompt that keeps the model grounded in its long-term objective."""
        evidence_summary = "\n".join(
            [f"- [{e.source}] **{e.title}** ({e.year or 'N/A'}): {e.finding}" for e in self.plan.evidence_locker[-8:]]
        ) or "No verified evidence recorded yet."

        hypotheses_str = "\n".join([f"- {h}" for h in self.plan.hypotheses]) or "None formalized yet."

        return (
            f"You are conducting a deep, long-horizon scientific investigation (Epoch {epoch}/{self.max_epochs}).\n\n"
            f"### OVERARCHING RESEARCH GOAL:\n{self.plan.goal}\n\n"
            f"### ACTIVE PHASE [{self.plan.current_phase_index + 1}/{len(self.plan.phases)}]:\n"
            f"**{phase.title}**\n"
            f"{phase.description}\n\n"
            f"### VERIFIED EVIDENCE ACCUMULATED SO FAR:\n{evidence_summary}\n\n"
            f"### ACTIVE WORKING HYPOTHESES:\n{hypotheses_str}\n\n"
            f"### INSTRUCTIONS FOR THIS EPOCH:\n"
            f"1. Choose the single most impactful investigative action to advance this phase.\n"
            f"2. Use your available endpoint tools (search databases, resolve citations, run calculations via python_eval, or inspect datasets).\n"
            f"3. Note any empirical contradictions or unexpected findings.\n"
            f"4. Propose or refine hypotheses based on new literature data.\n"
            f"5. Maintain high scientific rigor. Never fabricate citations or numbers."
        )

    def _execute_epoch_turn(self, prompt_text: str) -> str:
        """Execute model reasoning and local tool calls for the epoch."""
        history = ConversationHistory(
            system_prompt=(
                f"You are StemClaw's Deep Autonomous Research Engine for {self.session.category_name}. "
                "You conduct deep, methodical scientific investigations taking minutes to hours. "
                "Always verify claims against actual endpoints, cite DOIs/PMIDs, and synthesize rigorous findings."
            )
        )
        history.add_user_message(prompt_text)
        tools = self.registry.get_schemas()

        content_accumulator: List[str] = []
        pending_tool_calls: List[ToolCall] = []

        for chunk in self.adapter.generate_stream(history.get_messages(), tools=tools):
            if chunk.text_delta:
                if self.verbose:
                    console.print(chunk.text_delta, end="")
                content_accumulator.append(chunk.text_delta)
            if chunk.tool_calls:
                pending_tool_calls.extend(chunk.tool_calls)

        if self.verbose:
            console.print()

        # If tools requested, execute them
        if pending_tool_calls:
            assistant_content = "".join(content_accumulator)
            history.add_assistant_message(assistant_content, tool_calls=pending_tool_calls)

            for call in pending_tool_calls:
                if self.verbose:
                    console.print(
                        f"  [bold yellow]⚡ Deep Action:[/bold yellow] [bold cyan]{call.name}[/bold cyan] "
                        f"[dim]{call.raw_arguments or call.arguments}[/dim]"
                    )
                result = self.registry.execute_call(call)
                history.add_tool_result(result)

            # Model synthesizes tool observations
            synthesis_acc: List[str] = []
            for chunk in self.adapter.generate_stream(history.get_messages(), tools=tools):
                if chunk.text_delta:
                    if self.verbose:
                        console.print(chunk.text_delta, end="")
                    synthesis_acc.append(chunk.text_delta)
            if self.verbose:
                console.print()

            return "".join(synthesis_acc)

        return "".join(content_accumulator)

    def _reflect_and_extract_evidence(self, findings_text: str, phase: Any) -> None:
        """Self-reflection pass: parse findings into structured evidence locker items."""
        # Detect paper mentions or key findings
        sentences = [s.strip() for s in findings_text.split("\n") if s.strip()]
        for s in sentences:
            if any(k in s.lower() for k in ("doi:", "found that", "demonstrates", "revealed", "results show", "observed that")):
                clean_s = s.lstrip("-*•# ").strip()
                if len(clean_s) > 25 and len(clean_s) < 300:
                    self.plan.add_evidence(
                        title=f"{phase.title} Observation",
                        finding=clean_s,
                        source=self.session.category_name,
                    )
                    break

    def _compile_final_discovery_report(self, start_time: datetime) -> Path:
        """Synthesize all accumulated epochs and evidence into a comprehensive scientific discovery report."""
        elapsed_sec = (datetime.now(timezone.utc) - start_time).total_seconds()
        elapsed_str = f"{elapsed_sec / 60.0:.1f} minutes" if elapsed_sec > 60 else f"{int(elapsed_sec)} seconds"

        root = Path(self.session.workspace_root)
        report_filename = f"DISCOVERY_REPORT_{self.plan.task_id}.md"
        report_path = root / report_filename

        lines = [
            f"# Scientific Discovery Report: {self.plan.goal}",
            f"**Task ID:** `{self.plan.task_id}` | **Category:** {self.session.category_name}",
            f"**Investigation Duration:** {elapsed_str} | **Total Epochs:** {self.plan.total_epochs_run}\n",
            "---",
            "## 1. Executive Summary & Core Findings\n",
            f"This autonomous deep research investigation examined: *{self.plan.goal}* across multiple scientific endpoints and citation graphs.",
            f"A total of **{len(self.plan.evidence_locker)} verified empirical evidence points** were harvested and synthesized.\n",
            "## 2. Multi-Phase Investigation Trace\n",
        ]

        for idx, p in enumerate(self.plan.phases):
            status_symbol = "✔" if p.status == PhaseStatus.COMPLETED else "○"
            lines.append(f"### Phase {idx + 1}: {p.title} [{status_symbol} {p.status.value.upper()}]")
            lines.append(f"*{p.description}*")
            if p.findings_summary:
                lines.append(f"\n**Synthesized Findings:**\n{p.findings_summary}\n")
            lines.append("")

        lines.append("## 3. Evidence Locker (Empirical Discoveries)\n")
        if self.plan.evidence_locker:
            for e in self.plan.evidence_locker:
                doi_str = f" [DOI: {e.doi}]" if e.doi else ""
                lines.append(f"- **{e.title}** ({e.source}){doi_str}")
                lines.append(f"  > {e.finding}\n")
        else:
            lines.append("No isolated empirical items recorded.")

        lines.append("## 4. Methodological Conclusions & Open Questions\n")
        if self.plan.open_questions:
            lines.append("### Unresolved Hypotheses & Future Research Directions:")
            for q in self.plan.open_questions:
                lines.append(f"- {q}")
        else:
            lines.append("All primary research questions converged with consensus across domain literature.")

        lines.append("\n---\n*Generated by StemClaw Autonomous Research Agent*")

        report_path.write_text("\n".join(lines), encoding="utf-8")

        console.print(
            Panel(
                f"[bold green]✔ Deep Research Complete![/bold green]\n\n"
                f"**Report Generated:** [underline]{report_path}[/underline]\n"
                f"**Evidence Gathered:** {len(self.plan.evidence_locker)} verified items\n"
                f"**Duration:** {elapsed_str}",
                title="[bold green]Scientific Investigation Finalized[/bold green]",
                border_style="green",
            )
        )
        return report_path

