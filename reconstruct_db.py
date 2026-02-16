# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb",
# ]
# ///

import duckdb
import json
import urllib.request
import os

DB_FILENAME = "bambu_stock.duckdb"

def main():
    print("--- Bambu Stock DB Reconstructor ---")
    
    # 1. Fetch Manifest
    print("Fetching manifest...")
    manifest_url = "https://db-public.bbltracker.com/manifest.json"
    try:
        with urllib.request.urlopen(manifest_url) as response:
            manifest = json.loads(response.read())
    except Exception as e:
        print(f"Error fetching manifest: {e}")
        exit(1)

    # 2. Filter for Past 30 Days
    all_files = sorted(manifest['files'].keys())
    if not all_files:
        print("No files found in manifest.")
        exit(0)
        
    # Simple string comparison works for ISO dates YYYY-MM-DD
    from datetime import datetime, timedelta, timezone
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d')
    
    recent_files = [f for f in all_files if f >= cutoff_date]
    print(f"Found {len(all_files)} total shards.")
    print(f"Filtering for past 30 days (>= {cutoff_date})... {len(recent_files)} files selected.")
    
    if not recent_files:
        print("No recent files found.")
        exit(0)

    urls = [f"https://db-public.bbltracker.com/{f}" for f in recent_files]

    # 3. Create DuckDB File
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)
        print(f"Removed existing {DB_FILENAME}")

    print(f"Creating {DB_FILENAME}...")
    con = duckdb.connect(DB_FILENAME)
    
    # 4. Insert Data (Directly from remote Parquet to local DuckDB table)
    # This might take a few seconds depending on network.
    print("Downloading and merging data...")
    
    # We use CREATE TABLE AS SELECT ... FROM read_parquet([list_of_urls])
    # DuckDB handles the list of URLs natively.
    query = f"""
        CREATE TABLE stock_history AS 
        SELECT * FROM read_parquet({urls});
    """
    
    con.execute(query)
    
    # 5. Verify
    count = con.execute("SELECT count(*) FROM stock_history").fetchone()[0]
    print(f"Success! Imported {count} rows into '{DB_FILENAME}'.")
    
    con.close()
    
    print("\n[Next Steps]")
    print(f"1. Upload '{DB_FILENAME}' to ChatGPT (Code Interpreter).")
    print("2. Ask: 'Analyze the stock history in this file. When is Black PETG usually available?'")

if __name__ == "__main__":
    main()
