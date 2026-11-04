"""Persistent Research Scratchpad and Long-Term Memory for StemClaw."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from stemclaw.config import get_settings


@dataclass
class ResearchScratchpad:
    """Working memory and persistent notes for scientific investigations."""

    session_id: str = ""
    category: str = ""
    topic: str = ""
    findings: List[str] = field(default_factory=list)
    key_papers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def get_path(cls) -> Path:
        settings = get_settings()
        return settings.stemclaw_dir / "scratchpad.json"

    @classmethod
    def load(cls) -> "ResearchScratchpad":
        path = cls.get_path()
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return cls(**data)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        path = self.get_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.last_updated = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def add_finding(self, finding: str) -> None:
        """Add a verified scientific finding or takeaway to persistent memory."""
        cleaned = finding.strip()
        if cleaned and cleaned not in self.findings:
            self.findings.append(cleaned)
            self.save()

    def record_paper(
        self,
        paper_id: str,
        title: str,
        doi: Optional[str] = None,
        takeaway: Optional[str] = None,
    ) -> None:
        """Store a discovered paper and its key insight."""
        clean_id = paper_id.strip()
        if clean_id:
            self.key_papers[clean_id] = {
                "title": title.strip(),
                "doi": doi.strip() if doi else "",
                "takeaway": takeaway.strip() if takeaway else "",
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }
            self.save()

    def add_note(self, note: str) -> None:
        """Record an open hypothesis, question, or research step."""
        cleaned = note.strip()
        if cleaned:
            self.notes.append(cleaned)
            self.save()

    def clear(self) -> None:
        """Reset the scratchpad memory."""
        self.findings.clear()
        self.key_papers.clear()
        self.notes.clear()
        self.save()

    def format_summary(self) -> str:
        """Format scratchpad contents for rich display or agent prompt injection."""
        lines = []
        if self.topic:
            lines.append(f"**Research Topic:** {self.topic}")
        if self.findings:
            lines.append("\n**Key Findings & Evidence:**")
            for f in self.findings[-10:]:
                lines.append(f"  • {f}")
        if self.key_papers:
            lines.append("\n**Discovered Key Papers:**")
            for pid, info in list(self.key_papers.items())[-8:]:
                doi_str = f" ({info['doi']})" if info.get("doi") else ""
                takeaway_str = f" — {info['takeaway']}" if info.get("takeaway") else ""
                lines.append(f"  • [{pid}] {info['title']}{doi_str}{takeaway_str}")
        if self.notes:
            lines.append("\n**Research Notes & Next Steps:**")
            for n in self.notes[-5:]:
                lines.append(f"  - {n}")
        return "\n".join(lines) if lines else "(Research scratchpad is empty)"


_GLOBAL_SCRATCHPAD: Optional[ResearchScratchpad] = None


def get_scratchpad() -> ResearchScratchpad:
    global _GLOBAL_SCRATCHPAD
    if _GLOBAL_SCRATCHPAD is None:
        _GLOBAL_SCRATCHPAD = ResearchScratchpad.load()
    return _GLOBAL_SCRATCHPAD
