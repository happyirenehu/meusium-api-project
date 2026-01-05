import pandas as pd
import os

# ----------------- CONFIGURATION -----------------
# 1. FILE PATHS
RAW_CSV_FILE = 'raw_data.csv' 
FINAL_ARTWORK_CSV = 'leman_data/artwork_final.csv' # leman_data folder and files are purly for demestration only. The actual data scrip running in model.py is from the files in "data".
FINAL_ARTIST_CSV = 'leman_data/artist_final.csv'
FINAL_MEDIUM_CSV = 'leman_data/medium_final.csv' 

# 2. FILTER CRITERIA
# We will use this to find the collection data
COLLECTION_FILTER_COLUMN = 'Credit Line' # Assuming this column mentions the collection
COLLECTION_NAME = 'Robert Lehman Collection' 

# Secondary filter to guarantee the count is under 10,000
DATE_COLUMN = 'Object End Date' 
MIN_YEAR = 1600 # Extended the date range slightly for variety
MAX_YEAR = 2000

# 3. MAPPING COLUMNS
ARTIST_NAME_COLUMN = 'Artist Display Name' 
MEDIUM_NAME_COLUMN = 'Medium'

# ----------------- EXECUTION -----------------
def filter_and_save_data():
    print(f"--- Starting Data Filtering Process ---")
    
    # Setup and Loading Checks
    if not os.path.exists(RAW_CSV_FILE):
        print(f"❌ ERROR: Raw CSV file not found at '{RAW_CSV_FILE}'.")
        return
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created 'data' directory for output files.")

    try:
        df = pd.read_csv(RAW_CSV_FILE, low_memory=False)
        print(f"Raw file loaded. Total rows: {len(df)}")
    except Exception as e:
        print(f"❌ ERROR loading CSV: {e}")
        return

    # --- 1. Primary Filter: Search for 'Robert Lehman Collection' ---
    print(f"\n1. Primary Filter: Searching for '{COLLECTION_NAME}'...")
    
    # Use str.contains to find the collection name within the Credit Line column (case insensitive)
    df_filtered_collection = df[
        df[COLLECTION_FILTER_COLUMN].astype(str).str.contains(COLLECTION_NAME, case=False, na=False)
    ].copy()
    
    # --- Check if the collection filter alone is enough ---
    if len(df_filtered_collection) <= 10000:
        print(f"   -> Collection Filter only: {len(df_filtered_collection)} rows.")
        df_final_artwork = df_filtered_collection
    else:
        # --- 2. Secondary Filter: Apply Date Range (If Collection is too large) ---
        print("2. Secondary Filter: Applying Date Range as Collection is too large...")
        df_filtered_collection[DATE_COLUMN] = pd.to_numeric(df_filtered_collection[DATE_COLUMN], errors='coerce')
        
        df_final_artwork = df_filtered_collection[
            (df_filtered_collection[DATE_COLUMN] >= MIN_YEAR) & 
            (df_filtered_collection[DATE_COLUMN] <= MAX_YEAR)
        ].copy()
        print(f"   -> Final Artworks for the project: {len(df_final_artwork)} rows.")

    # --- 3. Create the Artist Table (Normalization) ---
    print("\n3. Creating Unique Artist List...")
    df_artists = pd.DataFrame(
        df_final_artwork[ARTIST_NAME_COLUMN].unique(), 
        columns=[ARTIST_NAME_COLUMN]
    )
    df_artists = df_artists.rename(columns={ARTIST_NAME_COLUMN: 'name'})
    df_artists = df_artists.dropna(subset=['name'])
    print(f"   -> Unique Artists for the project: {len(df_artists)} rows.")

    # --- 4. Create the Medium Category Table (Normalization) ---
    print("4. Creating Unique Medium Category List...")
    all_mediums = df_final_artwork[MEDIUM_NAME_COLUMN].dropna().unique()
    medium_set = set()
    for medium_list in all_mediums:
        for medium in medium_list.split(','):
            medium_set.add(medium.strip())

    df_mediums = pd.DataFrame(list(medium_set), columns=['name'])
    df_mediums = df_mediums[df_mediums['name'] != '']
    print(f"   -> Unique Medium Categories: {len(df_mediums)} rows.")

    # --- 5. Final Verification ---
    total_entries = len(df_final_artwork) + len(df_artists) + len(df_mediums)
    print(f"\n--- TOTAL FINAL ENTRIES (All Tables): {total_entries} ---")
    if total_entries <= 10000:
        print("✅ Yay! Total entries are within the 10,000 maximum.")
    else:
        print("❌ WARNING: Total entries exceed 10,000. Do something!")

    # --- 6. Save the Clean Data ---
    df_final_artwork.to_csv(FINAL_ARTWORK_CSV, index=False)
    df_artists.to_csv(FINAL_ARTIST_CSV, index=False)
    df_mediums.to_csv(FINAL_MEDIUM_CSV, index=False)
    print("\n--- All 3 Clean CSV Files Saved Successfully! ---")

if __name__ == "__main__":
    filter_and_save_data()