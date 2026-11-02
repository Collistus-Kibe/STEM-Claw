"""Built-in agent tools for file operations, citations, calculation, data inspection, and skills."""

from stemclaw.tools.builtins.citations import BibtexExportTool, FormatCitationTool
from stemclaw.tools.builtins.dataset_inspect import DatasetInspectTool
from stemclaw.tools.builtins.file_ops import FileReadTool, FileWriteTool, ListDirectoryTool
from stemclaw.tools.builtins.paper_cache import SearchLocalPapersTool
from stemclaw.tools.builtins.python_eval import PythonEvalTool
from stemclaw.tools.builtins.repos import SuggestRepoTool
from stemclaw.tools.builtins.skills import ActivateSkillTool

__all__ = [
    "FileReadTool",
    "FileWriteTool",
    "ListDirectoryTool",
    "SuggestRepoTool",
    "ActivateSkillTool",
    "BibtexExportTool",
    "FormatCitationTool",
    "PythonEvalTool",
    "DatasetInspectTool",
    "SearchLocalPapersTool",
]

