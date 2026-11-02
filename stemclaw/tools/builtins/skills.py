"""Tool allowing the agent to lazily activate and read skill bodies."""

from pydantic import BaseModel, Field
from stemclaw.skills.loader import get_skill_loader
from stemclaw.tools.base import BaseTool


class ActivateSkillInput(BaseModel):
    skill_name: str = Field(
        ...,
        description="Name of the active skill to load (e.g. 'literature-search-pubmed', 'arxiv-physics-literature')",
    )


class ActivateSkillTool(BaseTool):
    name = "activate_skill"
    description = (
        "Activate an armed procedural skill to load its comprehensive workflow, "
        "step-by-step instructions, and domain protocols into the agent context."
    )
    input_model = ActivateSkillInput

    def run(self, skill_name: str) -> str:
        loader = get_skill_loader()
        body = loader.get_skill_body(skill_name)
        if not body:
            return (
                f"Error: Skill '{skill_name}' is not currently loaded or could not be found. "
                f"Active loaded skills: {', '.join(loader._cached_skills.keys()) or 'None'}"
            )

        meta = loader._cached_skills[skill_name]
        return (
            f"=== ACTIVATED SKILL: {meta.name} (v{meta.version}) ===\n"
            f"Allowed Tools: {', '.join(meta.allowed_tools) or 'Any'}\n"
            f"Source: {meta.upstream}\n\n"
            f"{body}"
        )

