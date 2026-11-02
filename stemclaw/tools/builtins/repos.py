"""Tool to look up curated scientific knowledge repositories."""

from typing import Optional
from pydantic import BaseModel, Field
from stemclaw.config import get_settings
from stemclaw.session.router import STEMCategory, get_loadout
from stemclaw.session.state import SessionState
from stemclaw.tools.base import BaseTool


class SuggestRepoInput(BaseModel):
    topic: Optional[str] = Field(
        default=None,
        description="Optional filter keyword or research topic (e.g. 'genomics', 'materials', 'pinns')",
    )


class SuggestRepoTool(BaseTool):
    name = "suggest_repo"
    description = (
        "Retrieve curated GitHub knowledge repositories (datasets, pipelines, benchmarks) "
        "compiled for the active research category."
    )
    input_model = SuggestRepoInput

    def run(self, topic: Optional[str] = None) -> str:
        settings = get_settings()
        category = STEMCategory.LIFE_SCIENCES
        if SessionState.exists(settings.session_file):
            try:
                state = SessionState.load(settings.session_file)
                category = state.category
            except Exception:
                pass

        loadout = get_loadout(category)
        repos = loadout.knowledge_repos

        if topic:
            kw = topic.lower().strip()
            filtered = [
                r
                for r in repos
                if kw in r.name.lower()
                or kw in r.description.lower()
                or any(kw in t for t in r.topics)
            ]
            if filtered:
                repos = filtered

        lines = [f"Curated Knowledge Repositories for [{loadout.display_name}]:"]
        for r in repos:
            topics_str = f" [{', '.join(r.topics)}]" if r.topics else ""
            lines.append(f"• https://github.com/{r.name}{topics_str}\n  {r.description}")
        return "\n\n".join(lines)

