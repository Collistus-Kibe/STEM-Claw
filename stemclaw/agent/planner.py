"""Long-running research plan decomposition, checkpointing, and evidence management."""

import json
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from stemclaw.config import get_settings
from stemclaw.session.router import STEMCategory


class PhaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class EvidenceItem(BaseModel):
    """A verified scientific finding or data point discovered during deep research."""

    id: str = Field(default_factory=lambda: f"ev_{int(datetime.now().timestamp()*1000)%1000000:06d}")
    title: str
    source: str
    authors: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    finding: str
    relevance: str = "high"
    discovered_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ResearchPhase(BaseModel):
    """An explicit step in the autonomous scientific investigation roadmap."""

    id: str
    title: str
    description: str
    status: PhaseStatus = PhaseStatus.PENDING
    suggested_tools: List[str] = Field(default_factory=list)
    queries_executed: List[str] = Field(default_factory=list)
    findings_summary: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ResearchPlan(BaseModel):
    """The master roadmap governing a long-running research investigation over hours or days."""

    task_id: str
    goal: str
    category: STEMCategory
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: str = "active"  # "active", "completed", "paused"
    current_phase_index: int = 0
    total_epochs_run: int = 0
    phases: List[ResearchPhase] = Field(default_factory=list)
    evidence_locker: List[EvidenceItem] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    contradictions_observed: List[str] = Field(default_factory=list)

    @classmethod
    def create_for_goal(
        cls,
        goal: str,
        category: STEMCategory,
        task_id: Optional[str] = None,
    ) -> "ResearchPlan":
        """Generate a structured multi-phase investigation plan tailored to the domain."""
        if not task_id:
            slug = re.sub(r"[^a-z0-9]+", "_", goal.lower())[:24].strip("_")
            date_str = datetime.now().strftime("%Y%m%d_%H%M")
            task_id = f"task_{date_str}_{slug}"

        # Standard 5-phase scientific rigor roadmap
        phases = [
            ResearchPhase(
                id="phase_1_scoping",
                title="Hypothesis Scoping & Ontological Formulation",
                description="Deconstruct the research question into core hypotheses, candidate mechanisms, keyword variants, and domain constraints.",
                suggested_tools=["search_local_papers", "suggest_repo", "activate_skill"],
            ),
            ResearchPhase(
                id="phase_2_broad_survey",
                title="Multi-Repository Literature Harvesting",
                description="Perform exhaustive query harvesting across primary domain databases to identify pivotal publications and preprints.",
                suggested_tools=["arxiv_search", "ncbi_esearch", "semantic_scholar_search", "core_search", "gbif_occurrences"],
            ),
            ResearchPhase(
                id="phase_3_deep_citation_mining",
                title="Deep Citation Mining & Methodology Resolution",
                description="Traverse citation trees (forward/backward) for landmark papers, extract methodology details, and check open access full texts.",
                suggested_tools=["semantic_scholar_refs", "unpaywall_lookup", "crossref_search", "export_bibtex"],
            ),
            ResearchPhase(
                id="phase_4_data_validation",
                title="Empirical Data Validation & Synthesis",
                description="Verify reported quantitative results, run statistical sanity calculations via python_eval, or inspect workspace datasets.",
                suggested_tools=["python_eval", "dataset_inspect", "format_citation"],
            ),
            ResearchPhase(
                id="phase_5_discovery_synthesis",
                title="Comprehensive Discovery Report & Thesis Compilation",
                description="Synthesize all verified evidence into a publication-grade scientific discovery report with complete bibliography.",
                suggested_tools=["file_write", "export_bibtex"],
            ),
        ]

        return cls(
            task_id=task_id,
            goal=goal,
            category=category,
            phases=phases,
        )

    @property
    def current_phase(self) -> Optional[ResearchPhase]:
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None

    def advance_phase(self, summary: str = "") -> bool:
        """Mark current phase completed and advance to next phase."""
        now_iso = datetime.now(timezone.utc).isoformat()
        if self.current_phase:
            self.current_phase.status = PhaseStatus.COMPLETED
            self.current_phase.completed_at = now_iso
            if summary:
                self.current_phase.findings_summary = summary

        self.current_phase_index += 1
        self.updated_at = now_iso

        if self.current_phase_index < len(self.phases):
            self.phases[self.current_phase_index].status = PhaseStatus.IN_PROGRESS
            self.phases[self.current_phase_index].started_at = now_iso
            return True
        else:
            self.status = "completed"
            return False

    def add_evidence(
        self,
        title: str,
        finding: str,
        source: str = "literature",
        authors: Optional[str] = None,
        year: Optional[int] = None,
        doi: Optional[str] = None,
    ) -> EvidenceItem:
        """Record a verified empirical fact or paper finding."""
        item = EvidenceItem(
            title=title,
            finding=finding,
            source=source,
            authors=authors,
            year=year,
            doi=doi,
        )
        self.evidence_locker.append(item)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return item

    def get_task_dir(self, workspace_root: Optional[Path] = None) -> Path:
        """Get the filesystem storage directory for this long-running task."""
        settings = get_settings()
        root = workspace_root or settings.workspace_root
        task_dir = root / ".stemclaw" / "tasks" / self.task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir

    def save(self, workspace_root: Optional[Path] = None) -> Path:
        """Persist plan to disk checkpoint."""
        task_dir = self.get_task_dir(workspace_root)
        plan_file = task_dir / "plan.json"
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        return plan_file

    @classmethod
    def load(cls, task_id_or_path: str, workspace_root: Optional[Path] = None) -> "ResearchPlan":
        """Load an existing research plan from ID or file path."""
        p = Path(task_id_or_path)
        if not p.exists():
            settings = get_settings()
            root = workspace_root or settings.workspace_root
            p = root / ".stemclaw" / "tasks" / task_id_or_path / "plan.json"

        if not p.exists():
            raise FileNotFoundError(f"Research plan not found for '{task_id_or_path}' (checked '{p}')")

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

