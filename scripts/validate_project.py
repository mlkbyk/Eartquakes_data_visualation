"""Offline integrity checks; run: python scripts/validate_project.py"""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/earthquakes_dashboard_ready.csv"
METRICS = ROOT / "ml/reports/metrics.json"
SCORED = ROOT / "ml/reports/ml_scored_events.csv"
MAJOR = {"us6000jllz": 7.8, "us6000jlqa": 7.5}


def main():
    assert DATA.is_file(), f"Missing {DATA}"
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        assert len(fields) >= 7, f"Only {len(fields)} columns"
        mandatory = {"id", "time", "event_date_utc", "mag", "depth", "latitude", "longitude"}
        assert mandatory.issubset(fields), f"Missing {mandatory - set(fields)}"
        ids = set()
        mainshocks = {}
        n = 0
        for row in reader:
            n += 1
            event_id = row["id"]
            assert event_id not in ids, f"Duplicate event id: {event_id}"
            ids.add(event_id)
            if event_id in MAJOR:
                mainshocks[event_id] = row
    assert 2000 <= n <= 10000, f"Dataset outside agreed row range: {n}"
    assert set(mainshocks) == set(MAJOR), "Both Feb 6 mainshocks must be present"
    for event_id, magnitude in MAJOR.items():
        row = mainshocks[event_id]
        assert row["event_date_utc"].startswith("2023-02-06")
        assert abs(float(row["mag"]) - magnitude) < 1e-9
    print(f"PASS: {n:,} rows x {len(fields)} columns; IDs unique; Feb 6 mainshocks present")
    if METRICS.exists():
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))
        assert metrics["dataset"]["dataset_rows"] == n
        assert sum(metrics["kmeans"]["cluster_counts"].values()) == n
        assert metrics["dataset"]["train_rows"] + metrics["dataset"]["test_rows"] == n
        print("PASS: ML report row totals and cluster sizes")
    if SCORED.exists():
        with SCORED.open(encoding="utf-8", newline="") as f:
            rows = csv.DictReader(f)
            scored_ids = [r["id"] for r in rows]
        assert len(scored_ids) == n and set(scored_ids) == ids
        print("PASS: ML scoring IDs match prepared dataset")


if __name__ == "__main__":
    main()
