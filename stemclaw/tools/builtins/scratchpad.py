"""Built-in agent tools for persistent research scratchpad memory."""

from typing import Optional
from pydantic import BaseModel, Field

from stemclaw.tools.base import BaseTool


class MemorySaveInput(BaseModel):
    finding: Optional[str] = Field(
        default=None,
        description="A verified scientific finding, fact, or mechanism to save to memory",
    )
    paper_id: Optional[str] = Field(
        default=None,
        description="Paper PMID, DOI, or arXiv ID",
    )
    paper_title: Optional[str] = Field(
        default=None,
        description="Title of the paper being recorded",
    )
    takeaway: Optional[str] = Field(
        default=None,
        description="Key insight or clinical takeaway from this paper",
    )
    note: Optional[str] = Field(
        default=None,
        description="General research note, open question, or next step",
    )


class MemorySaveTool(BaseTool):
    name = "memory_save"
    description = (
        "Save a key finding, paper insight, or research note into persistent research scratchpad memory."
    )
    input_model = MemorySaveInput

    def run(
        self,
        finding: Optional[str] = None,
        paper_id: Optional[str] = None,
        paper_title: Optional[str] = None,
        takeaway: Optional[str] = None,
        note: Optional[str] = None,
    ) -> str:
        from stemclaw.agent.scratchpad import get_scratchpad
        scratchpad = get_scratchpad()
        saved_items = []

        if finding:
            scratchpad.add_finding(finding)
            saved_items.append("finding")

        if paper_id and paper_title:
            scratchpad.record_paper(paper_id, paper_title, takeaway=takeaway)
            saved_items.append("paper record")

        if note:
            scratchpad.add_note(note)
            saved_items.append("research note")

        if not saved_items:
            return "Notice: No items were provided to save to memory."

        return f"✔ Successfully saved {', '.join(saved_items)} to persistent research scratchpad."


class MemoryReadInput(BaseModel):
    section: Optional[str] = Field(
        default="all",
        description="Section to inspect: 'all', 'findings', 'papers', or 'notes'",
    )


class MemoryReadTool(BaseTool):
    name = "memory_read"
    description = (
        "Read verified findings, recorded papers, and active research notes from persistent scratchpad memory."
    )
    input_model = MemoryReadInput

    def run(self, section: str = "all") -> str:
        from stemclaw.agent.scratchpad import get_scratchpad
        scratchpad = get_scratchpad()
        sec = section.lower().strip()

        if sec == "findings":
            if not scratchpad.findings:
                return "No findings recorded in scratchpad yet."
            return "\n".join(f"• {f}" for f in scratchpad.findings)

        if sec == "papers":
            if not scratchpad.key_papers:
                return "No key papers recorded in scratchpad yet."
            lines = []
            for pid, info in scratchpad.key_papers.items():
                doi_str = f" ({info['doi']})" if info.get("doi") else ""
                lines.append(f"• [{pid}] {info['title']}{doi_str} — {info.get('takeaway', '')}")
            return "\n".join(lines)

        if sec == "notes":
            if not scratchpad.notes:
                return "No notes recorded in scratchpad yet."
            return "\n".join(f"- {n}" for n in scratchpad.notes)

        return scratchpad.format_summary()
