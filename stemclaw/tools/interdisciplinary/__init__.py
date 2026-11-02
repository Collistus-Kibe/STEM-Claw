"""Category 5: Interdisciplinary endpoint tools."""

from stemclaw.tools.interdisciplinary.core import CORESearchTool
from stemclaw.tools.interdisciplinary.unpaywall import UnpaywallLookupTool
from stemclaw.tools.interdisciplinary.doaj import DOAJSearchTool
from stemclaw.tools.interdisciplinary.zenodo import ZenodoSearchTool
from stemclaw.tools.interdisciplinary.figshare import FigshareSearchTool
from stemclaw.tools.interdisciplinary.osf import OSFPreprintsTool

__all__ = [
    "CORESearchTool",
    "UnpaywallLookupTool",
    "DOAJSearchTool",
    "ZenodoSearchTool",
    "FigshareSearchTool",
    "OSFPreprintsTool",
]

