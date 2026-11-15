"""Reproducible preparation of the 2023–2024 USGS earthquake CSV, including 6 February 2023.

Uses only Python's standard library. Preserves all original columns/values.
Filters to earthquakes in a complete-month date window: February 2023 through
May 2024, inclusive. Includes both Kahramanmaraş 6 February 2023 earthquakes. This keeps the project dataset under 10,000 rows
without random sampling or dropping rows with occasional missing metadata.

Usage:
    python prepare_earthquakes.py --input query.csv \
        --output data/earthquakes_dashboard_ready.csv
"""
import argparse
import csv
import datetime as dt
import math
from collections import Counter
from pathlib import Path

START = dt.datetime(2023, 2, 1, tzinfo=dt.timezone.utc)
END = dt.datetime(2024, 6, 1, tzinfo=dt.timezone.utc)  # exclusive
ADDED_COLS = [
    "event_date_utc", "event_year", "event_month", "event_year_month",
    "event_quarter", "event_weekday_utc", "event_hour_utc",
    "magnitude_band", "depth_category", "latitude_hemisphere",
    "latitude_band", "depth_exactly_10km",
]


def parse_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def magnitude_band(m):
    if m < 5.0: return "M4.5–4.9"
    if m < 6.0: return "M5.0–5.9"
    if m < 7.0: return "M6.0–6.9"
    return "M7.0+"


def depth_category(d):
    if d < 70: return "Shallow (<70 km)"
    if d < 300: return "Intermediate (70–299 km)"
    return "Deep (>=300 km)"


def latitude_band(lat):
    if lat < -60: return "60–90°S"
    if lat < -30: return "30–60°S"
    if lat < 0: return "0–30°S"
    if lat < 30: return "0–30°N"
    if lat < 60: return "30–60°N"
    return "60–90°N"


def prepare(input_path, output_path):
    with open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        original = reader.fieldnames or []
        required = {"time", "latitude", "longitude", "depth", "mag", "type", "id"}
        missing = required - set(original)
        if missing:
            raise ValueError(f"Required columns missing: {sorted(missing)}")
        if any(k in original for k in ADDED_COLS):
            raise ValueError("Already processed input; please provide original CSV")
        data = list(reader)

    out, ids, dropped_types, dropped_dates = [], set(), Counter(), 0
    for row in data:
        if row["type"] != "earthquake":
            dropped_types[row["type"]] += 1
            continue
        when = parse_time(row["time"])
        if not (START <= when < END):
            dropped_dates += 1
            continue
        if not row["id"] or row["id"] in ids:
            raise ValueError(f"Duplicate/missing ID within kept range: {row['id']}")
        ids.add(row["id"])
        lat, lon, depth, mag = (float(row[c]) for c in ("latitude", "longitude", "depth", "mag"))
        if not all(map(math.isfinite, (lat, lon, depth, mag))):
            raise ValueError(f"Non-finite core measurement for ID {row['id']}")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180 and depth >= -100 and mag >= 4.5):
            raise ValueError(f"Out-of-range core measurement for ID {row['id']}")
        out_row = {k: (row[k] or "").strip() for k in original}
        out_row.update({
            "event_date_utc": when.strftime("%Y-%m-%d"),
            "event_year": str(when.year),
            "event_month": str(when.month),
            "event_year_month": when.strftime("%Y-%m"),
            "event_quarter": f"{when.year}-Q{(when.month-1)//3+1}",
            "event_weekday_utc": when.strftime("%A"),
            "event_hour_utc": str(when.hour),
            "magnitude_band": magnitude_band(mag),
            "depth_category": depth_category(depth),
            "latitude_hemisphere": "Northern" if lat >= 0 else "Southern",
            "latitude_band": latitude_band(lat),
            # NOTE: 10 km can be a catalog-assigned default depth; this flag is NOT proof.
            "depth_exactly_10km": "True" if depth == 10.0 else "False",
        })
        out.append(out_row)

    if not (2000 <= len(out) <= 10000):
        raise ValueError(f"Project row constraint violated: {len(out)}")
    if len(original) + len(ADDED_COLS) < 7:
        raise ValueError("Project column constraint violated")

    out.sort(key=lambda r: (r["time"], r["id"]))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=original + ADDED_COLS)
        writer.writeheader()
        writer.writerows(out)
    print(f"INPUT: {len(data)} rows x {len(original)} columns")
    print(f"REMOVED_NON_EARTHQUAKES: {dict(dropped_types)}")
    print(f"REMOVED_OUTSIDE_WINDOW: {dropped_dates}")
    print(f"OUTPUT: {len(out)} rows x {len(original) + len(ADDED_COLS)} columns")
    print(f"UTC WINDOW: {START.isoformat()} to {END.isoformat()} (exclusive)")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="query.csv")
    parser.add_argument("--output", default="data/earthquakes_dashboard_ready.csv")
    args = parser.parse_args()
    prepare(args.input, args.output)
