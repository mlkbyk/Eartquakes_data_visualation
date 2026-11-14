# Data Dictionary (34 columns)

The first **22 columns are unmodified fields from the source USGS CSV**. The next **12 columns are derived for the dashboard**.

| Column | Meaning | Notes |
|---|---|---|
| `time` | Event timestamp (UTC) | Source ISO 8601 timestamp |
| `latitude` | Event latitude | Decimal degrees |
| `longitude` | Event longitude | Decimal degrees |
| `depth` | Event depth | Kilometers; 10 km may represent an assigned/fixed value |
| `mag` | Earthquake magnitude | M4.5+ selection; different `magType` values coexist |
| `magType` | Type/method of magnitude | Examples: mb, mww, mwr |
| `nst` | Number of stations contributing to location | Optional |
| `gap` | Largest azimuthal station gap | Degrees; optional |
| `dmin` | Minimum distance to a station | Catalog distance measure; optional |
| `rms` | RMS residual of travel-time solution | Source metric; not a direct earthquake impact score |
| `net` | Network identifier | Catalog metadata |
| `id` | Unique event identifier | Key for de-duplication |
| `updated` | Last catalog update timestamp | Not occurrence time |
| `place` | Human-readable event location description | Not a standardized country/administrative-region label |
| `type` | Event type | All retained values: `earthquake` |
| `horizontalError` | Horizontal location uncertainty | Optional, kilometers |
| `depthError` | Depth uncertainty | Kilometers |
| `magError` | Magnitude uncertainty | Optional |
| `magNst` | Stations used in magnitude estimate | Optional |
| `status` | Review status | All retained values: `reviewed` |
| `locationSource` | Network responsible for location | Metadata |
| `magSource` | Network responsible for magnitude | Metadata |
| `event_date_utc` | Derived YYYY-MM-DD event date | UTC |
| `event_year` | Derived event year | 2023/2024 (February 2023–May 2024 scope) |
| `event_month` | Derived event month | 1–12 |
| `event_year_month` | Derived YYYY-MM | Useful for monthly time series |
| `event_quarter` | Derived YYYY-Q# | Calendar quarter |
| `event_weekday_utc` | Day of week | Based on UTC, not local time |
| `event_hour_utc` | Hour of event | UTC 0–23 |
| `magnitude_band` | Magnitude category | M4.5–4.9, M5.0–5.9, M6.0–6.9, M7.0+ |
| `depth_category` | Depth category | Shallow <70; Intermediate 70–<300; Deep ≥300 km |
| `latitude_hemisphere` | North or South hemisphere | Based on latitude ≥0 |
| `latitude_band` | 30-degree latitudinal band | Six bands from 90°S to 90°N |
| `depth_exactly_10km` | Flag for depths exactly 10 km | **Possible**, not certain, fixed-depth cases |

Sources for definitions: https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php and https://earthquake.usgs.gov/earthquakes/search/
