---
name: "earthquake-event-analysis"
description: "Query and analyze seismic events, magnitude distributions, hypocentral depth profiling, Gutenberg-Richter b-values, and tectonic hazards via USGS API."
category: "earth_environmental"
allowed_tools:
  - usgs_earthquakes
  - suggest_repo
  - search_local_papers
  - python_eval
  - export_bibtex
required_keys: []
priority: 20
version: "2.0.0"
tags:
  - usgs
  - seismology
  - geophysics
  - earthquakes
  - natural-hazards
  - plate-tectonics
upstream: "K-Dense-AI/scientific-agent-skills"
---

# Earthquake Event Analysis & Geophysics Protocol

## 1. Overview & Geophysical Scope
This protocol governs the query, spatial clustering, magnitude distribution analysis, and tectonic hazard evaluation of seismic events using the USGS Real-Time Earthquake Hazards API. It distinguishes fault boundary mechanics, profiles hypocentral depths, identifies aftershock sequences, and calculates Gutenberg-Richter seismicity recurrence parameters.

---

## 2. Decision Tree & Seismic Analysis Pipeline

```
User Query (Region / Date Range / Minimum Magnitude)
  │
  ├── 1. Query USGS Earthquake API
  │     └─► Invoke `usgs_earthquakes(min_magnitude=..., start_time=..., end_time=...)`
  │           ├─► Hit: Extract event features (mag, place, time, depth_km, tsunami_flag)
  │           └─► Empty/Miss: Broaden geographic bounding box or lower magnitude threshold
  │
  ├── 2. Hypocentral Depth Profiling
  │     ├─► Shallow Crustal: Depth $< 70\text{ km}$ (highest ground shaking intensity, surface rupture)
  │     ├─► Intermediate: $70\text{ km} \le \text{Depth} < 300\text{ km}$ (Wadati-Benioff subducting slabs)
  │     └─► Deep Focus: Depth $\ge 300\text{ km}$ (phase transitions in mantle transition zone)
  │
  ├── 3. Tectonic Boundary & Mechanism Classification
  │     ├─► Convergent (Subduction Zones): Megathrust reverse faults (e.g. Cascadia, Japan Trench, Chile)
  │     ├─► Transform (Strike-Slip): Lateral displacement faults (e.g. San Andreas, North Anatolian)
  │     └─► Divergent (Rifting): Normal faulting and mid-ocean ridge spreading
  │
  ├── 4. Quantitative Seismological Calculations (`python_eval`)
  │     └─► Execute `python_eval` to compute:
  │           • Seismic Energy Release: $\log_{10} E = 4.8 + 1.5 M_w$ (Joules)
  │           • Energy Ratio: $\Delta E = 10^{1.5 \Delta M} \approx 31.62^{\Delta M}$
  │           • Gutenberg-Richter Recurrence: $\log_{10} N = a - bM$
  │
  └── 5. Tsunami & Secondary Hazard Evaluation
        └─► Check criteria: Magnitude $M_w \ge 7.0$ AND Shallow Depth $< 30\text{ km}$ AND Offshore submarine rupture
```

---

## 3. Adaptive Zero-Hit Query Fallback Matrix

| Condition | Cause | Remediation Action | Example |
| :--- | :--- | :--- | :--- |
| **0 events for regional name** | USGS does not filter by text place name | Use bounding box coordinates or query global catalog then filter | Query min_magnitude=4.5 without tight geographic strings |
| **0 events in short window** | Quiescent seismic interval | Expand temporal window from 24h to 7 days or 30 days | Increase start_time to 30 days prior |
| **High magnitude query empty** | Rare recurrence of $M \ge 7.0$ events | Lower magnitude cutoff to $M \ge 4.5$ or $M \ge 5.0$ to trace background seismicity | Replace $M \ge 7.5$ with $M \ge 5.0$ |
| **Missing depth parameter** | Preliminary unreviewed automated feed | Re-query with reviewed catalog feed status or note preliminary status | Explicitly flag event as `preliminary` |

---

## 4. Quantitative Seismology Calculations (`python_eval`)

Never estimate seismic energy release or Gutenberg-Richter parameters. Compute them via `python_eval`:

### A. Seismic Energy Scaling and Equivalent TNT
```python
def calculate_seismic_energy(mw: float):
    """Compute Gutenberg-Richter radiated seismic energy in Joules and equivalent TNT tons."""
    # log10(E) = 4.8 + 1.5 * Mw (Joules)
    log_e = 4.8 + 1.5 * mw
    energy_joules = 10 ** log_e
    tnt_joules = 4.184e9  # 1 ton of TNT = 4.184 * 10^9 J
    tnt_equivalent = energy_joules / tnt_joules
    print(f"Moment Magnitude Mw = {mw:.1f}")
    print(f"Radiated Energy: {energy_joules:.2e} Joules")
    print(f"Equivalent TNT: {tnt_equivalent:,.1f} metric tons")

# Compare M5.0 vs M7.0 vs M9.0
for mag in [5.0, 7.0, 9.0]:
    calculate_seismic_energy(mag)
    print("---")
```

### B. Gutenberg-Richter $b$-Value Estimation
```python
import math

def estimate_b_value(magnitudes: list, m_cutoff: float = 3.0) -> float:
    """Aki (1965) Maximum Likelihood estimate for Gutenberg-Richter b-value."""
    filtered = [m for m in magnitudes if m >= m_cutoff]
    if not filtered:
        return 0.0
    mean_m = sum(filtered) / len(filtered)
    # b = (log10(e)) / (mean(M) - (M_cutoff - delta_M / 2))
    b = math.log10(math.e) / (mean_m - m_cutoff)
    return b

# Example sample sequence
sample_mags = [3.1, 3.2, 3.5, 3.8, 4.0, 4.1, 4.5, 4.9, 5.2, 6.0]
b_val = estimate_b_value(sample_mags, m_cutoff=3.0)
print(f"Estimated Gutenberg-Richter b-value: {b_val:.2f} (Typical tectonic value ~ 1.0)")
```

---

## 5. Seismic Hazard Evidence Matrix Output Schema

Summarize earthquake catalogs using this standard evidence table:

| Event Identifier | Date & UTC Time | Magnitude ($M_w$) | Hypocenter Depth (km) | Focal Depth Class | Region / Epicenter | Tsunami Warning Flag | Secondary Hazards |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `us7000m3ab` | 2024-04-03 23:58:11 | 7.4 $M_w$ | 34.8 km | Shallow Crustal | Hualien, Taiwan | Yes (Issued) | Landslides, rockfalls, aftershock sequence |
| `nc73981245` | 2024-03-12 14:22:04 | 4.8 $M_w$ | 8.2 km | Shallow Crustal | San Jose, California | No | Minor shaking, no structural collapse |

---

## 6. Anti-Hallucination Rules & Negative Constraints
1. **Never Confuse Richter Local Magnitude ($M_L$) with Moment Magnitude ($M_w$)**: Modern seismological reporting standardizes on Moment Magnitude $M_w$, as $M_L$ saturates above $M \sim 6.5$. Always state the magnitude type.
2. **Never Predict Specific Earthquake Dates**: Explicitly adhere to geological consensus: earthquakes cannot be deterministically predicted with exact time and place. Only report probabilistic seismic hazard assessments (PSHA) and historical recurrence intervals.
3. **Verify Depth Ground Truth**: Shallow events ($< 20$ km) cause substantially higher surface acceleration (PGA) than deep events ($> 300$ km) of the same magnitude; never report magnitude without depth.
4. **BibTeX Archiving**: Proactively export citation metadata for relevant geophysical literature via `export_bibtex`.
