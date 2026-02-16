# Bambu Lab Store Filament Tracker Public Database

*https://bbltracker.com database for DuckDB and AI Queries*

The [Bambu Lab Store Filament Tracker](https://bbltracker.com) provides a public dataset of stock history, accessible via standard Parquet files. This data is updated approximately every 30 minutes.

## AI Assistant Usage

This documentation is designed to be machine-readable. You can paste this entire page into AI tools like **ChatGPT**, **Claude**, or **Gemini** to have them generate the correct DuckDB SQL queries for your analysis.

*Tip: Providing the Schema table below allows the AI to write precise queries for `timestamp`, `product_name`, and `stock` filtering.*

---

**Base URL**: `https://db-public.bbltracker.com`

## Quick Start (DuckDB)

You can query the data directly using DuckDB (CLI, Python, NodeJS, WASM).

```sql
-- Query a specific 6-hour block (e.g., Midnight - 6 AM on Feb 16, 2026)
SELECT * 
FROM read_parquet('https://db-public.bbltracker.com/2026-02-16-0000.parquet');
```

## Data Organization

The dataset uses a simplified "Micro-Iceberg" layout optimized for low-bandwidth discovery.

### 1. File Structure

Data is partitioned into **6-hour (UTC)** intervals to minimize file count while maintaining freshness.

*   **Pattern**: `YYYY-MM-DD-HHMM.parquet`
*   **Intervals**: `0000`, `0600`, `1200`, `1800`

```text
https://db-public.bbltracker.com/
├── manifest.json              <-- Entry point
├── 2026-02-15-1800.parquet    <-- Data (6pm - Midnight)
├── 2026-02-16-0000.parquet    <-- Data (Midnight - 6am)
├── 2026-02-16-0600.parquet    <-- Data (6am - Noon)
└── ...
```

### 2. The Manifest (`manifest.json`)

For programmatic discovery (e.g., AI Agents), read the `manifest.json` first. It serves as a comprehensive index of all available files.

**URL**: `https://db-public.bbltracker.com/manifest.json`

**Example Content**:
```json
{
  "generated": "2026-02-16T17:30:00.000Z",
  "files": {
    "2026-02-16-0000.parquet": { "rows": 1500 },
    "2026-02-16-0600.parquet": { "rows": 840 },
    "..."
  }
}
```

## Query Patterns

### Option A: Specific Time Range (Recommended)

Since the URL structure is deterministic (`YYYY-MM-DD-HH00`), you can calculate the filenames client-side without needing to list the bucket.

**Python Example: Scan all of February 2026**

```python
import duckdb

# Generate the list of URLs for every 6 hours in Feb 2026
urls = [
    f"https://db-public.bbltracker.com/2026-02-{day:02d}-{hour:02d}00.parquet"
    for day in range(1, 29)
    for hour in range(0, 24, 6)
]

# Query directly
df = duckdb.read_parquet(urls).df()
print(df.head())
```

### Option B: Full Manifest Scan
To analyze larger ranges, fetch the manifest to get the file list.

1.  GET `manifest.json`.
2.  Filter keys (filenames) by date range.
3.  Prepend base URL.
4.  Pass list to DuckDB.

## Schema

| Column | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | STRING | ISO 8601 Timestamp of the snapshot (UTC) |
| `product_name` | STRING | Name of the product family |
| `variant_name` | STRING | Specific variant name |
| `stock` | INTEGER | Quantity in stock |
| `region` | STRING | Region code (e.g., 'us', 'eu') |
| `eta` | STRING | Estimated arrival time (if available) |
| `max_quantity` | INTEGER | Purchase limit enforced by store |
| `is_flash_sale` | BOOLEAN | `true` if item is on flash sale |

---
