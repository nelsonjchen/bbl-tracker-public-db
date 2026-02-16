# Bambu Lab Store Filament Tracker Public Database

*https://bbltracker.com database for DuckDB and AI Queries*

The [Bambu Lab Store Filament Tracker](https://bbltracker.com) is based off a report generated from a DuckDB database. For bandwidth cost reasons, the database cannot be directly exposed. Instead, we provide a public streaming dataset of stock history, accessible via standard Parquet files. This data is updated every hour.

## Why Use This? 

*(Example: The "Black PETG" Bottleneck)*

Sometimes, simply knowing *if* an item is in stock isn't enough. You might want to know *when* multiple items are in stock together to save on shipping or validate a bulk order discount.

**Real-world Scenario:**
A [user on Reddit](https://www.reddit.com/r/BambuLab/comments/1qya5q4/comment/o4b505q/?context=3) wanted to order 4 specific filaments (White PLA Matte, Black PLA Matte, Rosewood PLA, and Black PETG) using a bulk discount. They had been waiting for 7 weeks because the items were never all in stock at the same time.

**The Agentic Query:**

By analyzing the history with an AI assistant such as Google Antigravity, we found the bottleneck:

The input was literally just the user's reddit post copy-pasted into the AI assistant.

> In the period from **Jan 31 to Feb 8**, there was **zero overlap** where all 4 items were in stock simultaneously. **Individual Availability (Jan 31 - Feb 8):**
>
> **PLA Matte White**: In stock ~24% of the time (50 hours total).
>
> **PLA Matte Black**: In stock ~31% of the time (65 hours total).
>
> **PLA Wood Rosewood**: In stock ~15% of the time (32 hours total).
>
> **PETG HF Black**: In stock **only ~0.7%** of the time (just 1.6 hours total). It seems the **Black PETG** is the main bottleneck, appearing for only very brief windows (less than 2 hours total in the last week). You might have better luck splitting your order or waiting for a larger restock event.

**The Solution:**

The analysis revealed that if the user dropped just the Black PETG from the order, the other 3 items had a **16-hour overlap window** where they could be purchased together. Black PETG can wait for another day.

This kind of complex, multi-variant temporal analysis is perfect for this dataset.

## AI Assistant Usage

Data analysis may not be your forte! Don't worry, we've got you covered. Use an AI assistant to generate the correct DuckDB SQL queries for your analysis.

This documentation is designed to be machine-readable. You can paste this entire page into AI tools like **ChatGPT**, **Claude**, or **Gemini** to have them generate the correct instructions and so on for your analysis.

Additionally, cloning this GitHub repository down, using Cursor, Antigravity, Claude Code, Gemini-CLI, OpenAI Codex, or any other assistant or tooling will allow you to perform deep analysis on the stock data.

If you don't even know how to start with that, it's OK to just paste this whole documentation into the ChatGPT, Gemini, Claude, or any other assistant or tooling to learn how to get the repository cloned onto a local machine.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/nelsonjchen/bbl-tracker-public-db) is also a good choice for querying with citations and references on how to use this repo but may be a bit less specific to your case. 

## Feedback & Accessibility

I understand that data analysis is technical, hard, and complicated. **My goal is to make this accessible and well-grounded for everyone.**

If you have feedback, find anomalies, or have ideas on how to make this easier to use, please **report it**. Whether it's a GitHub Issue or a comment on the subreddit, your feedback is crucial to making this "open data" experiment work for the community.

---

**Base URL**: `https://db-public.bbltracker.com`

---

## ⚠️ Data Caveats & Errata

### 1. Ingestion Start Times

Data collection started for different regions at different times. Early records may only contain US data.

| Region | Approximate Start Date | Notes |
| :--- | :--- | :--- |
| **US** | Jan 17, 2026 | Initial launch. |
| **EU, UK, AU, CA** | Jan 25, 2026* | |
| **Global (Rest of Asia not including JP or KR)** | Feb 01, 2026* | |

### 2. Stock Visibility Caps

The Bambu Lab store frontend often caps the reported stock quantity for performance or anti-scraping reasons.
*   **Common Caps**:
    *   `10`: Often seen during **Flash Sales** (where per-customer limits are low).
    *   `200`: Early global cap used across all regions.
    *   `400`: Standard cap for large regions (US, EU) in recent data.
*   **Implication**: If a row reports `stock = 200`, the *real* stock is likely `200+`. You should treat these values as "at least X".
*   **Max Quantity Column**: The `max_quantity` column often reflects this store-imposed limit.

**Timeline of Constraints:**
*   **Before Feb 03, 2026**: Unlimited / Uncapped (visible stock was likely somewhat accurate).
*   **Feb 03 - Feb 09, 2026**: Global cap at 200.
*   **After Feb 09, 2026**: Variable family-based caps (typically 10, 200, or 400) depending on region or SKU state.

### 3. Sampling Rate

*   **Jan 17 - Feb 14, 2026**: ~60-minute intervals.
*   **Feb 14, 2026 - Present**: ~30-minute intervals, aligned to the hour plus 5 minutes.

---
## FAQ & Technical Details

### 1. Pricing Data
**We do not track pricing.** This tool is strictly for tracking stock availability. If pricing is your primary concern, standard store browsing is recommended.

### 2. Linking to Store Pages
The dataset does not include direct URLs to save space. You will need to match `product_name` and `variant_name` to the store's frontend manually.

**Tip:** When programmatically accessing store pages, append `?skr=yes` to the URL. This cookie/parameter tells the store to **bypass the region selection redirect**, allowing you to view stock for other regions without being forced back to your local store.

### 3. Missing Rows vs. Stock 0
*   **Stock = 0**: The item was scanned and confirmed to be **Out of Stock**.
*   **Row Missing**: The item was not found in the scan (e.g., removed from the store listing entirely or a temporary network error).

### 4. License
This dataset is provided under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** license.

### 5. Hosting & Rate Limits
This data is hosted on **Cloudflare R2**. feel free to use it within Cloudflare's own reasonable and generous download limits.

---

## Quick Start (DuckDB)

You can query the data directly using DuckDB (CLI, Python, NodeJS, WASM).

### ⚡ Rapid Start (Python with `uv`)

We highly recommend using [uv](https://docs.astral.sh/uv/) for a fast, zero-setup experience. We've included a [script.py](script.py) example in this repo.

1.  **Install `uv`** (if you haven't already):
    *   *Mac/Linux*: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   *Windows/Other*: See [official installation docs](https://docs.astral.sh/uv/getting-started/installation/).
2.  **Run the example**:
    ```bash
    # Automatically installs duckdb/pandas and runs the query
    uv run script.py
    ```

### SQL Example

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
