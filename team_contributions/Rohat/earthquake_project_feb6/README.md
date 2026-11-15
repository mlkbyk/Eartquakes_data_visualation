# SEISMOSCOPE — Global Earthquake Data Exploration, with 6 February 2023 Kahramanmaraş case study

## About the data

- **Source:** U.S. Geological Survey (USGS), ANSS Comprehensive Earthquake Catalog (ComCat).
- **Catalog:** https://earthquake.usgs.gov/earthquakes/search/
- **Dataset:** `data/earthquakes_dashboard_ready.csv` — **9,889 rows × 34 columns**, 22 original fields plus 12 derived fields.
- **Period (UTC):** February 1, 2023 (inclusive) through June 1, 2024 (exclusive) — 16 complete months.
- **Coverage:** Worldwide earthquakes of magnitude **4.5 or higher**, with `status = reviewed` in this supplied catalog.
- **Main case study:** 6 February 2023 Kahramanmaraş earthquakes (M7.8 Pazarcık and M7.5 Elbistan), both present by their verified USGS event IDs.
- **Original upload:** `query.csv` — 13,472 records, 22 columns. The original source is not modified or included in this package.

### Why this time frame?

The previous cleaned dataset covered July 2023–November 2024 and unintentionally excluded the major February 6 earthquakes. This version retains **all** M4.5+ earthquakes in the continuous February 2023–May 2024 time window, rather than randomly sampling rows. It remains under the 10,000-row project constraint.

### Reproduce the preparation

```bash
python prepare_earthquakes.py --input query.csv --output data/earthquakes_dashboard_ready.csv
```

Uses Python 3 standard library only. The CSV preserves the original measurements and event IDs; extra fields support visualization. Optional source metadata are not imputed.

### Major 6 February 2023 events (Türkiye local time UTC+3)

| Event | Magnitude | Local time | USGS event ID |
|---|---:|---|---|
| Pazarcık | 7.8 | 04:17 | `us6000jllz` |
| Elbistan | 7.5 | 13:24 | `us6000jlqa` |

Official event pages: https://earthquake.usgs.gov/earthquakes/eventpage/us6000jllz and https://earthquake.usgs.gov/earthquakes/eventpage/us6000jlqa

The small `data/kahramanmaras_6feb_major_events_reference.csv` lists only these two verified event rows; it is **not** the 2,000+ row project dataset.

### Scientific and data limitations

- Only **M4.5+** records are included, not all smaller aftershocks.
- A regional coordinate/date filter does not establish membership in the Kahramanmaraş aftershock sequence.
- The dataset has 11 months in 2023 and 5 months in 2024; annual raw totals must not be compared as if periods were equal.
- Many records have depth 10 km; USGS warns some depths can be fixed to 10 km if poorly determined.
- There are no fatalities, exposure, damage or building fragility fields; do not interpret the catalog as a full earthquake risk dataset.

### Included files

- `data/earthquakes_dashboard_ready.csv` — ready dataset (9,889 × 34)
- `data/kahramanmaras_6feb_major_events_reference.csv` — two official reference events
- `docs/VERI_KALITE_RAPORU.md` — Turkish validation report
- `docs/DATA_DICTIONARY.md` — 34-column field definitions
- `docs/VISUALIZATION_PLAN.md` — nine chart ideas and two exploratory ML methods
- `docs/quality_metrics.json` — programmatic data checks
- `prepare_earthquakes.py` — reproducible preparation script

### Source and usage

USGS-published datasets are generally U.S. public-domain materials, subject to dataset-specific notes. Credit the **U.S. Geological Survey (USGS), ANSS Comprehensive Earthquake Catalog (ComCat)** and link original event records. No endorsement is implied.

### Remaining CEN445 work

Build the interactive Streamlit dashboard (9 distinct visualization types, at least 6 advanced types, 3+ controls), optional two basic ML analyses, team contribution notes, and one-page English report / presentation.
