"""StemClaw session state persistence and management."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from stemclaw.config import get_settings
from stemclaw.session.router import STEMCategory, get_loadout


# Default built-in agent tools present across all loadouts (Claude Code style)
BUILTIN_AGENT_TOOLS = [
    "file_read",
    "file_write",
    "file_edit",
    "shell_exec",
    "web_fetch",
    "list_directory",
    "search_files",
    "suggest_repo",
    "activate_skill",
    "export_bibtex",
    "format_citation",
    "python_eval",
    "dataset_inspect",
    "search_local_papers",
]


class SessionState(BaseModel):
    """Serializable runtime state of the current research session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: STEMCategory
    category_code: int
    category_name: str
    visual_theme: str
    procedural_symbol: str
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    workspace_root: str
    active_tools: List[str] = Field(default_factory=list)
    active_skills: List[str] = Field(default_factory=list)
    active_repos: List[str] = Field(default_factory=list)
    suggested_keys: List[str] = Field(default_factory=list)
    is_active: bool = True

    @classmethod
    def create_for_category(
        cls,
        category: STEMCategory,
        workspace_root: Optional[Path] = None,
    ) -> "SessionState":
        """Instantiate a new session state with category loadouts applied."""
        loadout = get_loadout(category)
        settings = get_settings()
        root = workspace_root or settings.workspace_root

        # Combine builtins with category endpoint tools
        all_tools = list(BUILTIN_AGENT_TOOLS) + list(loadout.endpoint_tools)
        repo_names = [r.name for r in loadout.knowledge_repos]

        # Discover and load vendored skills using SkillLoader (strict 8-skill cap)
        from stemclaw.skills.loader import get_skill_loader
        loader = get_skill_loader()
        loaded_skills = loader.load_skills_for_category(category, max_skills=8)
        skill_names = [s.name for s in loaded_skills]
        if not skill_names:
            skill_names = list(loadout.default_skills[:8])

        return cls(
            category=category,
            category_code=loadout.code,
            category_name=loadout.display_name,
            visual_theme=loadout.visual_theme,
            procedural_symbol=loadout.procedural_symbol,
            workspace_root=str(root.resolve()),
            active_tools=all_tools,
            active_skills=skill_names[:8],  # strict 8-skill cap
            active_repos=repo_names,
            suggested_keys=list(loadout.suggested_keys),
        )

    def save(self, target_path: Optional[Path] = None) -> Path:
        """Write session state to session.json."""
        if target_path:
            path = target_path
        elif self.workspace_root:
            path = Path(self.workspace_root) / ".stemclaw" / "session.json"
        else:
            settings = get_settings()
            path = settings.session_file
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        return path

    @classmethod
    def load(cls, source_path: Optional[Path] = None) -> "SessionState":
        """Read session state from session.json."""
        settings = get_settings()
        path = source_path or settings.session_file
        if not path.exists():
            raise FileNotFoundError(f"Session file not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    @classmethod
    def exists(cls, path: Optional[Path] = None) -> bool:
        """Check if an existing active session file is on disk."""
        settings = get_settings()
        p = path or settings.session_file
        return p.exists() and p.stat().st_size > 0
