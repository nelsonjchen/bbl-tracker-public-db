# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb",
#     "pandas",
# ]
# ///

import duckdb
import json
import urllib.request

# 1. Fetch the manifest to discover available files
print("Fetching manifest...")
manifest_url = "https://db-public.bbltracker.com/manifest.json"
try:
    with urllib.request.urlopen(manifest_url) as response:
        manifest = json.loads(response.read())
except Exception as e:
    print(f"Error fetching manifest: {e}")
    exit(1)

# 2. Select the most recent files (e.g., last 24 hours / 4 files)
all_files = sorted(manifest['files'].keys())
if not all_files:
    print("No files found in manifest.")
    exit(0)

recent_files = all_files[-4:]
urls = [f"https://db-public.bbltracker.com/{f}" for f in recent_files]

print(f"Querying {len(urls)} recent files:\n" + "\n".join([f" - {u}" for u in urls]))

# 3. Agentic Query: "Find Availability Bottlenecks"
# Challenge: "I want to buy multiple items. Which one is holding up my order?"
# Solution: Calculate the % of time each item is in stock (availability score).

print(f"Querying {len(urls)} recent files for Availability Stats (US Region)...")

query = f"""
    WITH subset AS (
        SELECT 
            timestamp,
            product_name || ' - ' || variant_name as full_name,
            stock,
            max_quantity
        FROM read_parquet({urls})
        WHERE region = 'us'
    ),
    stats AS (
        SELECT
            full_name,
            COUNT(*) as total_snapshots,
            SUM(CASE WHEN stock > 0 THEN 1 ELSE 0 END) as in_stock_snapshots,
            MAX(stock) as max_stock_seen,
            MAX(max_quantity) as cap_seen
        FROM subset
        GROUP BY full_name
    )
    SELECT
        full_name,
        ROUND((in_stock_snapshots::FLOAT / total_snapshots) * 100, 1) as availability_pct,
        max_stock_seen,
        cap_seen
    FROM stats
    WHERE availability_pct > 0  -- Filter out completely dead items for noise reduction
    ORDER BY availability_pct ASC -- Show bottlenecks first
    LIMIT 15;
"""

print("\n--- Availability Report (Bottleneck Detection) ---")
# Use an in-memory database connection
con = duckdb.connect()
df = con.execute(query).df()

print(df.to_string(index=False))

print("\n[Analysis] Items with low availability % are likely your 'Black PETG' bottlenecks.")
