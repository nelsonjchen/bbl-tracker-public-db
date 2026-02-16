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

# 3. Query with DuckDB
query = f"""
    SELECT 
        timestamp, 
        region, 
        product_name, 
        stock,
        max_quantity
    FROM read_parquet({urls})
    WHERE stock > 0
    ORDER BY timestamp DESC
    LIMIT 10
"""

print("\nExecuting Query...")
# Use an in-memory database connection
con = duckdb.connect()
df = con.execute(query).df()

print("\n--- Recent In-Stock Items ---")
print(df.to_string(index=False))
