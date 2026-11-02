"""Skill loader with frontmatter parsing, collision detection, and 8-skill hard cap."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from pydantic import BaseModel, Field

from stemclaw.config import get_settings
from stemclaw.session.router import STEMCategory

logger = logging.getLogger("stemclaw.skills")


class SkillMetadata(BaseModel):
    """Frontmatter metadata extracted from a SKILL.md file."""

    name: str = Field(..., description="Unique kebab-case skill identifier")
    description: str = Field(..., description="Summary of procedural skill capabilities")
    category: str = Field(..., description="Target STEM category")
    allowed_tools: List[str] = Field(default_factory=list)
    required_keys: List[str] = Field(default_factory=list)
    priority: int = Field(default=5, description="1 (highest) to 10 (lowest) for tiebreaks")
    version: str = Field(default="1.0.0")
    tags: List[str] = Field(default_factory=list)
    upstream: str = Field(default="K-Dense-AI/scientific-agent-skills")
    file_path: Optional[Path] = Field(default=None, exclude=True)


class SkillLoader:
    """Manages discovery, validation, collision handling, and lazy loading of skills."""

    def __init__(self, skills_dir: Optional[Path] = None) -> None:
        settings = get_settings()
        self.skills_dir = skills_dir or (settings.workspace_root / "skills")
        self._cached_skills: Dict[str, SkillMetadata] = {}
        self._collision_logs: List[str] = []

    @property
    def collision_logs(self) -> List[str]:
        return list(self._collision_logs)

    def parse_skill_file(self, file_path: Path) -> Optional[SkillMetadata]:
        """Parse only the YAML frontmatter of a SKILL.md without loading full body."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if not content.startswith("---"):
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            frontmatter_raw = parts[1]
            data = yaml.safe_load(frontmatter_raw)
            if not isinstance(data, dict):
                return None

            metadata = SkillMetadata.model_validate(data)
            metadata.file_path = file_path.resolve()
            return metadata
        except Exception as e:
            logger.warning(f"Failed to parse skill at {file_path}: {e}")
            return None

    def load_skills_for_category(
        self,
        category: STEMCategory,
        max_skills: int = 8,
    ) -> List[SkillMetadata]:
        """Discover and load skills for a category adhering to the strict 8-skill cap."""
        candidates_by_name: Dict[str, SkillMetadata] = {}
        cat_str = category.value

        search_roots = [
            self.skills_dir / cat_str,
            self.skills_dir,
        ]

        # Scan for SKILL.md files
        seen_paths = set()
        for root in search_roots:
            if not root.exists():
                continue
            for skill_path in root.glob("**/SKILL.md"):
                resolved = skill_path.resolve()
                if resolved in seen_paths:
                    continue
                seen_paths.add(resolved)

                meta = self.parse_skill_file(skill_path)
                if not meta or meta.category != cat_str:
                    continue

                # Collision detection: higher priority (lower number) wins
                if meta.name in candidates_by_name:
                    existing = candidates_by_name[meta.name]
                    if meta.priority < existing.priority:
                        log_msg = (
                            f"Skill collision for '{meta.name}': replacing priority "
                            f"{existing.priority} with {meta.priority} from {skill_path.name}"
                        )
                        self._collision_logs.append(log_msg)
                        logger.info(log_msg)
                        candidates_by_name[meta.name] = meta
                    else:
                        log_msg = (
                            f"Skill collision for '{meta.name}': keeping priority "
                            f"{existing.priority} over {meta.priority} from {skill_path.name}"
                        )
                        self._collision_logs.append(log_msg)
                        logger.info(log_msg)
                else:
                    candidates_by_name[meta.name] = meta

        # Sort candidate skills by priority (ascending) and then by name
        sorted_candidates = sorted(
            candidates_by_name.values(),
            key=lambda s: (s.priority, s.name),
        )

        # Enforce strict 8-skill hard cap
        if len(sorted_candidates) > max_skills:
            excess = sorted_candidates[max_skills:]
            excess_names = [s.name for s in excess]
            cap_msg = (
                f"Exceeded hard cap of {max_skills} skills for loadout '{cat_str}'. "
                f"Refusing to load {len(excess)} skills: {', '.join(excess_names)}"
            )
            self._collision_logs.append(cap_msg)
            logger.warning(cap_msg)
            active_skills = sorted_candidates[:max_skills]
        else:
            active_skills = sorted_candidates

        # Cache active skills for lazy body retrieval
        for s in active_skills:
            self._cached_skills[s.name] = s

        return active_skills

    def get_skill_body(self, skill_name: str) -> Optional[str]:
        """Lazily read and return the full markdown procedure of an active skill."""
        meta = self._cached_skills.get(skill_name)
        if not meta or not meta.file_path or not meta.file_path.exists():
            return None

        content = meta.file_path.read_text(encoding="utf-8", errors="replace")
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
        return content.strip()


_LOADER_INSTANCE: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """Retrieve the singleton skill loader."""
    global _LOADER_INSTANCE
    if _LOADER_INSTANCE is None:
        _LOADER_INSTANCE = SkillLoader()
    return _LOADER_INSTANCE

