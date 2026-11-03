"""Tool registry for registering, discovering, and dispatching tool calls."""

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from stemclaw.session.router import STEMCategory
from stemclaw.tools.base import BaseTool, ToolCall, ToolResult
from stemclaw.tools.builtins import (
    ActivateSkillTool,
    BibtexExportTool,
    DatasetInspectTool,
    FileReadTool,
    FileWriteTool,
    FormatCitationTool,
    ListDirectoryTool,
    PythonEvalTool,
    SearchLocalPapersTool,
    SuggestRepoTool,
)
from stemclaw.tools.life_sciences import (
    BioRxivSearchTool,
    EuropePMCSearchTool,
    NCBIEfetchTool,
    NCBIEsearchTool,
    OrcidLookupTool,
    UniProtSearchTool,
)
from stemclaw.tools.physical_sciences import (
    ArxivSearchTool,
    ChemblSearchTool,
    CrossrefSearchTool,
    DoePagesSearchTool,
    OpenAlexSearchTool,
    PubchemSearchTool,
)
from stemclaw.tools.engineering_cs import (
    DBLPSearchTool,
    SemanticScholarSearchTool,
    SemanticScholarRefsTool,
    PapersWithCodeTool,
    GithubSearchTool,
    IEEEXploreTool,
)
from stemclaw.tools.earth_environmental import (
    GBIFOccurrencesTool,
    GBIFSpeciesTool,
    NASAMediaSearchTool,
    NOAAClimateDataTool,
    USGSEarthquakesTool,
    CopernicusDataTool,
)
from stemclaw.tools.interdisciplinary import (
    CORESearchTool,
    UnpaywallLookupTool,
    DOAJSearchTool,
    ZenodoSearchTool,
    FigshareSearchTool,
    OSFPreprintsTool,
)


class ToolRegistry:
    """Registry that manages loaded tools and dispatches execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Look up tool by name."""
        return self._tools.get(name)

    def list_names(self) -> List[str]:
        """Return list of registered tool names."""
        return list(self._tools.keys())

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Export all tool schemas in Meta Llama / OpenAI function format."""
        return [tool.to_schema() for tool in self._tools.values()]

    def execute_call(self, call: ToolCall) -> ToolResult:
        """Execute a tool call requested by the model with pre/post hooks."""
        from stemclaw.session.hooks import get_hook_manager

        tool = self.get(call.name)
        if tool is None:
            return ToolResult(
                call_id=call.id,
                name=call.name,
                output=f"Error: Tool '{call.name}' is not registered or loaded in this session.",
                is_error=True,
            )

        args = dict(call.arguments)
        if not args and call.raw_arguments:
            try:
                args = json.loads(call.raw_arguments)
            except Exception as e:
                return ToolResult(
                    call_id=call.id,
                    name=call.name,
                    output=f"Error: Invalid JSON arguments: {e}",
                    is_error=True,
                )

        # PreToolUse security & injection gate
        hook_mgr = get_hook_manager()
        decision = hook_mgr.pre_tool_use(tool, ToolCall(id=call.id, name=call.name, arguments=args))
        if not decision.proceed:
            return ToolResult(
                call_id=call.id,
                name=call.name,
                output=decision.rejection_reason or "Tool call rejected by security policy.",
                is_error=True,
            )

        effective_args = decision.modified_arguments if decision.modified_arguments is not None else args
        result = tool.execute(**effective_args)
        result.call_id = call.id

        # PostToolUse callback
        hook_mgr.post_tool_use(tool, call, result)
        return result

    @classmethod
    def create_for_category(cls, category: STEMCategory) -> "ToolRegistry":
        """Instantiate a registry populated with category endpoints and builtins."""
        reg = cls()

        # Builtins (always active across all STEM categories)
        reg.register(FileReadTool())
        reg.register(FileWriteTool())
        reg.register(ListDirectoryTool())
        reg.register(SuggestRepoTool())
        reg.register(ActivateSkillTool())
        reg.register(BibtexExportTool())
        reg.register(FormatCitationTool())
        reg.register(PythonEvalTool())
        reg.register(DatasetInspectTool())
        reg.register(SearchLocalPapersTool())

        # Category 1: Life Sciences
        if category == STEMCategory.LIFE_SCIENCES:
            # Core domain endpoints
            reg.register(NCBIEsearchTool())
            reg.register(NCBIEfetchTool())
            reg.register(EuropePMCSearchTool())
            reg.register(BioRxivSearchTool())
            reg.register(UniProtSearchTool())
            reg.register(OrcidLookupTool())
            # Cross-category endpoints
            reg.register(PubchemSearchTool())
            reg.register(ChemblSearchTool())
            reg.register(OpenAlexSearchTool())
            reg.register(CrossrefSearchTool())
            reg.register(UnpaywallLookupTool())
            reg.register(GithubSearchTool())
            reg.register(ArxivSearchTool())
            reg.register(SemanticScholarSearchTool())
            reg.register(CORESearchTool())

        # Category 2: Physical Sciences
        elif category == STEMCategory.PHYSICAL_SCIENCES:
            # Core domain endpoints
            reg.register(ArxivSearchTool())
            reg.register(OpenAlexSearchTool())
            reg.register(CrossrefSearchTool())
            reg.register(DoePagesSearchTool())
            reg.register(ChemblSearchTool())
            reg.register(PubchemSearchTool())
            # Cross-category endpoints
            reg.register(UnpaywallLookupTool())
            reg.register(GithubSearchTool())
            reg.register(SemanticScholarSearchTool())
            reg.register(CORESearchTool())
            reg.register(EuropePMCSearchTool())
            reg.register(USGSEarthquakesTool())

        # Category 3: Engineering & CS
        elif category == STEMCategory.ENGINEERING_CS:
            # Core domain endpoints
            reg.register(DBLPSearchTool())
            reg.register(SemanticScholarSearchTool())
            reg.register(SemanticScholarRefsTool())
            reg.register(PapersWithCodeTool())
            reg.register(GithubSearchTool())
            reg.register(IEEEXploreTool())
            # Cross-category endpoints
            reg.register(ArxivSearchTool())
            reg.register(OpenAlexSearchTool())
            reg.register(CrossrefSearchTool())
            reg.register(UnpaywallLookupTool())
            reg.register(CORESearchTool())

        # Category 4: Earth & Environmental
        elif category == STEMCategory.EARTH_ENVIRONMENTAL:
            # Core domain endpoints
            reg.register(GBIFOccurrencesTool())
            reg.register(GBIFSpeciesTool())
            reg.register(NASAMediaSearchTool())
            reg.register(NOAAClimateDataTool())
            reg.register(USGSEarthquakesTool())
            reg.register(CopernicusDataTool())
            # Cross-category endpoints
            reg.register(OpenAlexSearchTool())
            reg.register(CrossrefSearchTool())
            reg.register(BioRxivSearchTool())
            reg.register(ArxivSearchTool())
            reg.register(UnpaywallLookupTool())
            reg.register(GithubSearchTool())
            reg.register(CORESearchTool())

        # Category 5: Interdisciplinary
        elif category == STEMCategory.INTERDISCIPLINARY:
            # Core domain endpoints
            reg.register(CORESearchTool())
            reg.register(UnpaywallLookupTool())
            reg.register(DOAJSearchTool())
            reg.register(ZenodoSearchTool())
            reg.register(FigshareSearchTool())
            reg.register(OSFPreprintsTool())
            # Cross-category endpoints
            reg.register(OpenAlexSearchTool())
            reg.register(CrossrefSearchTool())
            reg.register(GithubSearchTool())
            reg.register(ArxivSearchTool())
            reg.register(BioRxivSearchTool())
            reg.register(EuropePMCSearchTool())
            reg.register(SemanticScholarSearchTool())
            reg.register(PubchemSearchTool())

        return reg


_REGISTRIES_BY_CATEGORY: Dict[STEMCategory, ToolRegistry] = {}


def get_default_registry(category: Optional[STEMCategory] = None) -> ToolRegistry:
    """Return the tool registry for the given category (defaults to Life Sciences)."""
    cat = category or STEMCategory.LIFE_SCIENCES
    if cat not in _REGISTRIES_BY_CATEGORY:
        _REGISTRIES_BY_CATEGORY[cat] = ToolRegistry.create_for_category(cat)
    return _REGISTRIES_BY_CATEGORY[cat]

