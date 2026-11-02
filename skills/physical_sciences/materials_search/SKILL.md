---
name: "materials-property-lookup"
description: "Identification of crystal structures, space groups, phase stability, bandgaps, and electronic transport properties via DOE PAGES and OpenAlex."
category: "physical_sciences"
allowed_tools:
  - doe_pages_search
  - openalex_search
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 2
version: "2.0.0"
tags:
  - materials-science
  - crystallography
  - doe-pages
  - solid-state-physics
  - energy-materials
  - semiconductors
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Materials Property & Crystallography Lookup Protocol

## 1. Overview & Materials Scope
This protocol governs the identification, crystallographic characterization, phase equilibrium assessment, and electronic/transport property analysis of solid-state materials, battery electrolytes, photovoltaic perovskites, and functional ceramics using DOE PAGES and OpenAlex. It enforces standard Hermann-Mauguin space group notations, validates DFT vs experimental measurements, and deterministically calculates solid-state physical constants.

---

## 2. Decision Tree & Materials Pipeline

```
User Query (Chemical Formula / Material Class / System)
  │
  ├── 1. Check Local Cache & Previous Runs
  │     └─► `search_local_papers(query="<FORMULA> crystal structure")`
  │           ├─► Hit: Extract crystal system, space group, lattice constants
  │           └─► Miss: Proceed to step 2
  │
  ├── 2. Query Primary Energy & Physics Repositories
  │     ├─► DOE PAGES: `doe_pages_search(query="<FORMULA> bandgap crystal structure", rows=5)`
  │     └─► OpenAlex: `openalex_search(query="<FORMULA> perovskite solid electrolyte", rows=5)`
  │
  ├── 3. Crystallographic & Structural Parameter Extraction
  │     ├─► Crystal System: Cubic, Tetragonal, Orthorhombic, Hexagonal, Trigonal, Monoclinic, Triclinic
  │     ├─► Space Group: Hermann-Mauguin symbol (e.g. $Pm\bar{3}m$, $I4/mcm$, $Fd\bar{3}m$) & International Table #
  │     ├─► Lattice Parameters: $a, b, c$ (in Å) and angles $\alpha, \beta, \gamma$ (in degrees)
  │     └─► Density / Cell Volume: Unit cell volume $V = \mathbf{a} \cdot (\mathbf{b} \times \mathbf{c})$
  │
  ├── 4. Quantitative Physical Property Evaluation
  │     └─► Execute `python_eval` to compute:
  │           • Optical absorption cutoff: $\lambda = \frac{1239.8419}{E_g}\text{ nm}$
  │           • Theoretical X-ray density: $\rho = \frac{Z \cdot M}{N_A \cdot V}$
  │           • Arrhenius activation energy for ionic conduction: $\sigma T = \sigma_0 e^{-E_a / k_B T}$
  │
  └── 5. Empirical vs Density Functional Theory (DFT) Reconciliation
        └─► Disclose exchange-correlation functional (PBE, HSE06, SCAN, GW) vs experimental XRD/optical measurements
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Cause | Remediation Action | Example Query |
| :--- | :--- | :--- | :--- |
| **0 hits on non-stoichiometric formula** | Doped composition too specific | Query end-member parent phase and dopant mechanism | `Li6.5La3Zr1.5Ta0.5O12` $\rightarrow$ `LLZO garnet` OR `Li7La3Zr2O12` |
| **0 hits on perovskite nickname** | Informal acronym not in indexed titles | Query stoichiometric formula or IUPAC chemical name | `MAPbI3` $\rightarrow$ `CH3NH3PbI3` OR `methylammonium lead iodide` |
| **Ambiguous polymorph phase** | Multiple temperature/pressure phases exist | Specify room temperature / ambient pressure phase | `TiO2 rutile vs anatase` |
| **DOE PAGES rate-limit or timeout** | High traffic on national lab API | Fall back to `openalex_search` with materials concept filter | Query OpenAlex with DOI or materials topic tags |

---

## 4. Quantitative Materials Calculations (`python_eval`)

Never estimate bandgap wavelengths, unit cell volumes, or theoretical densities. Calculate them with `python_eval`:

### A. Bandgap to Optical Cutoff Wavelength ($\lambda$)
```python
def bandgap_to_wavelength(eg_ev: float) -> float:
    """Convert semiconductor bandgap (eV) to optical cutoff wavelength (nm) using hc constant."""
    hc_ev_nm = 1239.84193
    return hc_ev_nm / eg_ev

# Examples of key energy materials
materials = {
    "Silicon (Si)": 1.12,
    "Gallium Arsenide (GaAs)": 1.42,
    "MAPbI3 Perovskite": 1.55,
    "Titanium Dioxide (TiO2 Rutile)": 3.03,
    "Gallium Nitride (GaN)": 3.40
}

for name, eg in materials.items():
    wavelength = bandgap_to_wavelength(eg)
    print(f"{name}: Eg = {eg:.2f} eV -> Cutoff Wavelength = {wavelength:.1f} nm")
```

### B. Theoretical X-ray Density Calculation
```python
def calculate_xray_density(z_formula_units: int, molar_mass: float, volume_angstrom3: float) -> float:
    """Compute crystal density in g/cm^3 from unit cell parameters."""
    avogadro = 6.02214076e23
    volume_cm3 = volume_angstrom3 * 1e-24
    density = (z_formula_units * molar_mass) / (avogadro * volume_cm3)
    return density

# Example: Cubic SrTiO3 (a = 3.905 A, Z = 1, M = 183.49 g/mol)
vol = 3.905 ** 3
rho = calculate_xray_density(1, 183.49, vol)
print(f"SrTiO3 Unit Cell Volume: {vol:.2f} A^3 | Theoretical Density: {rho:.3f} g/cm^3")
```

---

## 5. Materials Evidence Matrix Output Schema

Summarize materials characterizations using this standard evidence table:

| Chemical System | Crystal System | Space Group (Symbol / #) | Lattice Constants (Å) | Bandgap $E_g$ (eV) | Measurement Type | Key Functional Application | DOI / Source |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| $\text{CH}_3\text{NH}_3\text{PbI}_3$ | Tetragonal (RT) | $I4/mcm$ (#140) | $a=8.85$, $c=12.64$ | 1.55 eV (Direct) | Optical absorption | Photovoltaic absorber | 10.1038/nphoton.2014.134 |
| $\text{Li}_7\text{La}_3\text{Zr}_2\text{O}_{12}$ | Cubic | $Ia\bar{3}d$ (#230) | $a=12.97$ | $\approx 6.0\text{ eV}$ (Insulating) | Impedance spectroscopy | Solid-state Li battery electrolyte | 10.1002/anie.200702783 |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Confuse DFT Generalized Gradient (GGA-PBE) with Experimental Bandgaps**: Standard PBE systematically underestimates semiconductor bandgaps by 30–50%. Explicitly distinguish PBE, HSE06, and experimental UV-Vis/optical spectroscopy values.
2. **Space Group Precision**: Always report space groups in proper Hermann-Mauguin notation (e.g., $Pm\bar{3}m$, not "Pm3m" or "cubic").
3. **Specify Temperature & Phase**: Many materials undergo structural phase transitions (e.g. BaTiO3 is cubic above 120°C, tetragonal at room temperature). Always state the measurement temperature.
4. **BibTeX Archiving**: Proactively call `export_bibtex` when seminal crystallographic or materials papers are retrieved.
