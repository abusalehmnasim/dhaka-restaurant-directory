import pandas as pd
import os
import glob

print("Starting merge process...\n")

# ── Step 1: Load existing OSM data ─────────────────────────────────────────────
osm_df = pd.read_csv("dhaka_restaurants.csv", encoding="utf-8-sig")
print(f"OSM data loaded: {len(osm_df)} places")

# ── Step 2: Column mapping for each Excel file ─────────────────────────────────
# Maps each file's columns to our standard column names
FILE_CONFIG = {
    "Gulshan_Food_Directory.xlsx": {
        "area_col"   : "Area",
        "default_area": "Gulshan"
    },
    "Uttara_Food_Directory.xlsx": {
        "area_col"   : "Sector / Area",
        "default_area": "Uttara"
    },
    "Mirpur_Restaurants_v2.xlsx": {
        "area_col"   : "Area / Section",
        "default_area": "Mirpur",
        "exclude_col": "Excluded?"
    },
}

# ── Step 3: Load and standardize each Excel file ───────────────────────────────
all_excel = []

for filename, config in FILE_CONFIG.items():
    filepath = os.path.join("excel_data", filename)
    if not os.path.exists(filepath):
        print(f"  ⚠️  File not found: {filepath} — skipping")
        continue

    print(f"\nLoading: {filename}")
    df = pd.read_excel(filepath, header=1)

    # Remove excluded rows if column exists
    if "exclude_col" in config and config["exclude_col"] in df.columns:
        before = len(df)
        df = df[df[config["exclude_col"]].isna()]
        print(f"  Excluded {before - len(df)} flagged rows")

    # Rename area column to standard
    if config["area_col"] in df.columns:
        df = df.rename(columns={config["area_col"]: "Area"})

    # Standardize columns
    df = df.rename(columns={
        "Cuisine Type"       : "Cuisine",
        "Google\nRating"     : "Google Rating",
        "No. of\nReviews"    : "Google Reviews",
        "Price\nRange"       : "Price Range",
        "Opening Hours"      : "Opening Hours",
        "Phone Number"       : "Phone",
        "Special Notes"      : "Special Notes",
        "Place Type (Google)": "Google Place Type",
        "Google Types"       : "Google Place Type",
    })

    # Add source tag
    df["Source"] = "Manual Research"
    df["Type"] = df.get("Category", pd.Series(["Restaurant"] * len(df)))

    # Fill area if missing
    df["Area"] = df["Area"].fillna(config["default_area"])

    # Keep only relevant columns
    keep_cols = [
        "Name", "Type", "Cuisine", "Area", "Address",
        "Phone", "Opening Hours", "Google Rating",
        "Google Reviews", "Price Range", "Special Notes",
        "Latitude", "Longitude"
    ]
    available = [c for c in keep_cols if c in df.columns]
    df = df[available]

    # Drop rows with no name
    df = df[df["Name"].notna() & (df["Name"].str.strip() != "")]

    print(f"  Loaded {len(df)} places from {filename}")
    all_excel.append(df)

if not all_excel:
    print("\nNo Excel files found in excel_data/ folder. Exiting.")
    exit()

# ── Step 4: Combine all Excel data ─────────────────────────────────────────────
excel_combined = pd.concat(all_excel, ignore_index=True)
print(f"\nTotal from Excel files: {len(excel_combined)} places")

# ── Step 5: Add missing OSM columns to Excel data ─────────────────────────────
for col in osm_df.columns:
    if col not in excel_combined.columns:
        excel_combined[col] = "N/A"

# Add missing Excel columns to OSM data
for col in excel_combined.columns:
    if col not in osm_df.columns:
        osm_df[col] = "N/A"

# ── Step 6: Deduplicate — remove Excel entries already in OSM ─────────────────
osm_names = set(osm_df["Name"].str.lower().str.strip())

def is_duplicate(name):
    return str(name).lower().strip() in osm_names

excel_new = excel_combined[~excel_combined["Name"].apply(is_duplicate)]
excel_dupes = len(excel_combined) - len(excel_new)
print(f"Duplicates found in OSM data: {excel_dupes}")
print(f"New unique places from Excel: {len(excel_new)}")

# ── Step 7: Merge ──────────────────────────────────────────────────────────────
osm_df["Source"] = "OpenStreetMap"
merged = pd.concat([osm_df, excel_new], ignore_index=True)
merged.drop_duplicates(subset=["Name", "Address"], inplace=True)
merged["Name"] = merged["Name"].astype(str)
merged.sort_values("Name", inplace=True)
merged.reset_index(drop=True, inplace=True)

# ── Step 8: Save ───────────────────────────────────────────────────────────────
merged.to_csv("dhaka_restaurants.csv", index=False, encoding="utf-8-sig")
merged.to_excel("dhaka_restaurants.xlsx", index=False)

print(f"\n{'='*50}")
print(f"  MERGE COMPLETE!")
print(f"{'='*50}")
print(f"  OSM places          : {len(osm_df)}")
print(f"  New from Excel      : {len(excel_new)}")
print(f"  Duplicates skipped  : {excel_dupes}")
print(f"  Total merged        : {len(merged)}")
print(f"{'='*50}")
print(f"\n  Files updated:")
print(f"  -> dhaka_restaurants.csv")
print(f"  -> dhaka_restaurants.xlsx")