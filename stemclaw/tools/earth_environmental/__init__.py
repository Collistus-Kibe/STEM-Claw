"""Category 4: Earth & Environmental endpoint tools."""

from stemclaw.tools.earth_environmental.gbif import (
    GBIFOccurrencesTool,
    GBIFSpeciesTool,
)
from stemclaw.tools.earth_environmental.nasa import NASAMediaSearchTool
from stemclaw.tools.earth_environmental.noaa import NOAAClimateDataTool
from stemclaw.tools.earth_environmental.usgs import USGSEarthquakesTool
from stemclaw.tools.earth_environmental.copernicus import CopernicusDataTool

__all__ = [
    "GBIFOccurrencesTool",
    "GBIFSpeciesTool",
    "NASAMediaSearchTool",
    "NOAAClimateDataTool",
    "USGSEarthquakesTool",
    "CopernicusDataTool",
]

