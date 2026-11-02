"""Category 3: Engineering & Computer Science endpoint tools."""

from stemclaw.tools.engineering_cs.dblp import DBLPSearchTool
from stemclaw.tools.engineering_cs.semantic_scholar import (
    SemanticScholarSearchTool,
    SemanticScholarRefsTool,
)
from stemclaw.tools.engineering_cs.papers_with_code import PapersWithCodeTool
from stemclaw.tools.engineering_cs.github_search import GithubSearchTool
from stemclaw.tools.engineering_cs.ieee_xplore import IEEEXploreTool

__all__ = [
    "DBLPSearchTool",
    "SemanticScholarSearchTool",
    "SemanticScholarRefsTool",
    "PapersWithCodeTool",
    "GithubSearchTool",
    "IEEEXploreTool",
]

