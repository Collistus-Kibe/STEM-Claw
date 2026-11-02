---
name: species-taxonomy-mapping
description: Resolve organism nomenclature, taxonomic classification hierarchies, and geospatial biodiversity occurrence patterns via GBIF.
category: earth_environmental
allowed_tools:
  - gbif_species
  - gbif_occurrences
  - suggest_repo
  - export_bibtex
  - python_eval
  - dataset_inspect
required_keys: []
priority: 10
version: "2.0.0"
tags:
  - biodiversity
  - gbif
  - taxonomy
  - ecology
  - geospatial
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Species Taxonomy & Geospatial Biodiversity Mapping

## 1. Overview & Objectives
Standardize biological nomenclature according to the Linnaean backbone taxonomy and extract validated geospatial observation records from GBIF (Global Biodiversity Information Facility).

---

## 2. Procedural Workflow

```
[Organism Vernacular / Common Name]
        │
        ▼
[Step 1: Resolve Accepted Binomial via `gbif_species(query=...)`]
        │
        ├──► Verify Status: ACCEPTED vs SYNONYM vs HOMONYM
        │
        ▼
[Step 2: Map Full Backbone Hierarchy (Kingdom to Species)]
        │
        ▼
[Step 3: Query Geospatial Occurrences via `gbif_occurrences(query=..., limit=10)`]
        │
        ├──► Filter Null Island (0,0) and Default Country Centroids
        │
        ▼
[Step 4: Compute Latitudinal / Temporal Distribution Envelope via `python_eval`]
        │
        ▼
[Step 5: Synthesize Ecological Profile & Habitat Envelope]
```

### Step 1: Nomenclature Disambiguation
- Query `gbif_species` with the organism name.
- Verify whether the returned record has status `ACCEPTED`. If `SYNONYM`, redirect to the accepted canonical binomial name.
- Record the canonical GBIF taxon key (`key`).

### Step 2: Coordinate Quality Control
When analyzing records from `gbif_occurrences`:
- Filter out coordinates at `(0.0, 0.0)` ("Null Island").
- Differentiate observation basis: `HUMAN_OBSERVATION` vs `PRESERVED_SPECIMEN` vs `MACHINE_OBSERVATION` vs `FOSSIL_SPECIMEN`.

### Step 3: Biogeographic Envelope Calculation
- Use `python_eval` to calculate bounding coordinate ranges (min/max latitude, min/max longitude) and elevation bounds.

---

## 3. Biodiversity Presentation Schema

```markdown
### Taxonomic Classification
- **Accepted Binomial:** *Panthera onca* (Linnaeus, 1758)
- **Hierarchy:** Animalia > Chordata > Mammalia > Carnivora > Felidae > *Panthera*
- **Taxonomic Status:** ACCEPTED (GBIF ID: 5219426)

### Geospatial Distribution & Occurrence Sample
| Region / Country | Coordinates (Lat, Lon) | Basis of Record | Date / Year | Dataset |
|---|---|---|---|---|
| Brazil (Amazonas) | (-3.465, -62.215) | HUMAN_OBSERVATION | 2023-08 | iNaturalist Research-grade |
| Mexico (Quintana Roo) | (19.521, -87.982) | PRESERVED_SPECIMEN | 2019-11 | UNAM Specimen Collection |

### Bioclimatic & Conservation Summary
- **Habitat Envelope:** Tropical and subtropical moist broadleaf forests, wetlands.
- **Occurrence Density Trend:** High density in Amazonian basin, fragmented corridors in Central America.
```
