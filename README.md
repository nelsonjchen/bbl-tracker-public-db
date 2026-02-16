# Bambu Lab Store Filament Tracker Public Database

*https://bbltracker.com database for DuckDB and AI Queries*

The [Bambu Lab Store Filament Tracker](https://bbltracker.com) is based off a report generated from a DuckDB database. For bandwidth cost reasons, the database cannot be directly exposed. Instead, we provide a public dataset of stock history, accessible via standard Parquet files. This data is updated every hour.

## Why Use This? (Example: The "Black PETG" Bottleneck)

Sometimes, simply knowing *if* an item is in stock isn't enough. You might want to know *when* multiple items are in stock together to save on shipping or validat a bulk order discount.

**Real-world Scenario:**
A [user on Reddit](https://www.reddit.com/r/BambuLab/comments/1qya5q4/comment/o4b505q/?context=3) wanted to order 4 specific filaments (White PLA Matte, Black PLA Matte, Rosewood PLA, and Black PETG) using a bulk discount. They had been waiting for 7 weeks because the items were never all in stock at the same time.

**The Agentic Query:**
By analyzing the history with an AI agent, we found the bottleneck:
> "In the period from Jan 31 to Feb 8... Black PETG is definitely the bottleneck. It seems to be a global thing... appearing for only very brief windows (less than 2 hours total in the last week)."

**The Solution:**
The analysis revealed that if the user dropped just the Black PETG from the order, the other 3 items had a **16-hour overlap window** where they could be purchased together. This kind of complex, multi-variant temporal analysis is perfect for this dataset.

## AI Assistant Usage

Data analysis may not be your forte! Don't worry, we've got you covered. Use an AI assistant to generate the correct DuckDB SQL queries for your analysis.

This documentation is designed to be machine-readable. You can paste this entire page into AI tools like **ChatGPT**, **Claude**, or **Gemini** to have them generate the correct instructions and so on for your analysis.

Additionally, cloning this GitHub repository down, using Cursor, Antigravity, Claude Code, Gemini-CLI, OpenAI Codex, or any other assistant or tooling will allow you to perform deep analysis on the stock data.

If you don't even know how to start with that, it's OK to just paste this whole documentation into the ChatGPT, Gemini, Claude, or any other assistant or tooling to learn how to get the repository cloned onto a local machine.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/nelsonjchen/bbl-tracker-public-db) is also a good choice for querying with citations and references but may be a bit less specific to your case.

---

**Base URL**: `https://db-public.bbltracker.com`

---

## ⚠️ Data Caveats & Errata

### 1. Ingestion Start Times

Data collection started for different regions at different times. Early records may only contain US data.

| Region | Approximate Start Date | Notes |
| :--- | :--- | :--- |
| **US** | Jan 17, 2026 | Initial launch. |
| **EU, UK, AU, CA** | Jan 25, 2026* | *Estimated based on available history.* |
| **JP, Global** | Feb 01, 2026* | *Estimated.* |

### 2. Stock Visibility Caps ("The 50/400 Limit")

The Bambu Lab store frontend often caps the reported stock quantity for performance or anti-scraping reasons.
*   **Common Caps**:
    *   `10`: Often seen during **Flash Sales** (where per-customer limits are low).
    *   `200`: Early global cap used across all regions.
    *   `400`: Standard cap for large regions (US, EU) in recent data.
*   **Implication**: If a row reports `stock = 50`, the *real* stock might be 50, 500, or 5000. You should treat these values as "at least X".
*   **Max Quantity Column**: The `max_quantity` column often reflects this store-imposed limit.

**Timeline of Constraints:**
*   **Before Feb 03, 2026**: Unlimited / Uncapped (visible stock was accurate).
*   **Feb 03 - Feb 09, 2026**: Global cap at 200.
*   **After Feb 09, 2026**: Variable family-based caps (typically 50, 400, or 1000).

### 3. Sampling Rate

*   **Jan 17 - Feb 14, 2026**: ~30-minute intervals.
*   **Feb 14, 2026 - Present**: ~60-minute intervals (aligned to the hour).

---

## Quick Start (DuckDB)

You can query the data directly using DuckDB (CLI, Python, NodeJS, WASM).

```sql
-- Query a specific 6-hour block (e.g., Midnight - 6 AM UTC on Feb 16, 2026) 
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
