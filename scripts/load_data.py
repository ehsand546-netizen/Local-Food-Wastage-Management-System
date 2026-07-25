"""
load_data.py
------------------
This script reads our 4 CSV files using pandas and loads
their data into the corresponding SQL tables we created earlier.

Run this AFTER create_tables.py has been run once.
"""

import pandas as pd
import sqlite3
import os

# Path to our existing database (created in create_tables.py)
db_path = os.path.join("database", "food_wastage.db")

# Connect to the database
conn = sqlite3.connect(db_path)

# ---------------------------------------------------------
# Load providers_data.csv into the 'providers' table
# ---------------------------------------------------------
providers_df = pd.read_csv(os.path.join("data", "providers_data.csv"))
# if_exists="replace" means: clear the table first, then insert fresh data
# This makes the script safe to re-run without creating duplicate rows
providers_df.to_sql("providers", conn, if_exists="replace", index=False)
print(f"Loaded {len(providers_df)} rows into 'providers' table")

# ---------------------------------------------------------
# Load receivers_data.csv into the 'receivers' table
# ---------------------------------------------------------
receivers_df = pd.read_csv(os.path.join("data", "receivers_data.csv"))
receivers_df.to_sql("receivers", conn, if_exists="replace", index=False)
print(f"Loaded {len(receivers_df)} rows into 'receivers' table")

# ---------------------------------------------------------
# Load food_listings_data.csv into the 'food_listings' table
# ---------------------------------------------------------
food_df = pd.read_csv(os.path.join("data", "food_listings_data.csv"))
food_df.to_sql("food_listings", conn, if_exists="replace", index=False)
print(f"Loaded {len(food_df)} rows into 'food_listings' table")

# ---------------------------------------------------------
# Load claims_data.csv into the 'claims' table
# ---------------------------------------------------------
claims_df = pd.read_csv(os.path.join("data", "claims_data.csv"))
claims_df.to_sql("claims", conn, if_exists="replace", index=False)
print(f"Loaded {len(claims_df)} rows into 'claims' table")

# Close the connection
conn.close()

print("\nAll data loaded successfully into the database!")