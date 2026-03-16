import os
import datetime
import requests
import pandas as pd
import json
import re
import os
from collections import Counter

print("Starting data collection...")
print("Please wait, this may take 30-60 seconds.\n")

# ── STEP 1: Fetch data ─────────────────────────────────────────────────────────
overpass_url = "https://overpass.kumi.systems/api/interpreter"
query = """
[out:json][timeout:90];
(
  node["amenity"="restaurant"](23.68,90.33,23.90,90.50);
  node["amenity"="cafe"](23.68,90.33,23.90,90.50);
  node["amenity"="fast_food"](23.68,90.33,23.90,90.50);
  node["amenity"="food_court"](23.68,90.33,23.90,90.50);
  way["amenity"="restaurant"](23.68,90.33,23.90,90.50);
  way["amenity"="cafe"](23.68,90.33,23.90,90.50);
  way["amenity"="fast_food"](23.68,90.33,23.90,90.50);
);
out body;
>;
out skel qt;
"""

try:
    print("Connecting to OpenStreetMap...")
    response = requests.get(overpass_url, params={"data": query}, timeout=120)
    response.raise_for_status()
    data = response.json()
    print(f"Raw data received. Total elements: {len(data['elements'])}\n")

except requests.exceptions.Timeout:
    print("ERROR: Request timed out. Check your internet and try again.")
    exit()
except requests.exceptions.ConnectionError:
    print("ERROR: No internet connection.")
    exit()
except Exception as e:
    print(f"ERROR: Something went wrong - {e}")
    exit()


# ── STEP 2: Thana/Area bounding boxes ─────────────────────────────────────────
# Format: "Area Name": (min_lat, min_lon, max_lat, max_lon)
AREA_BOXES = {
    # ── North ──────────────────────────────────────────
    "Uttara"           : (23.860, 90.385, 23.905, 90.415),
    "Uttara West"      : (23.860, 90.360, 23.905, 90.386),
    "Bashundhara"      : (23.810, 90.420, 23.860, 90.460),
    "Cantonment"       : (23.800, 90.395, 23.840, 90.425),
    "Pallabi"          : (23.820, 90.345, 23.862, 90.385),

    # ── Northwest ──────────────────────────────────────
    "Mirpur"           : (23.790, 90.345, 23.825, 90.380),
    "Mirpur DOHS"      : (23.820, 90.370, 23.845, 90.395),
    "Kafrul"           : (23.790, 90.375, 23.820, 90.400),

    # ── West ───────────────────────────────────────────
    "Mohammadpur"      : (23.755, 90.352, 23.790, 90.378),
    "Shyamoli"         : (23.765, 90.353, 23.787, 90.373),
    "Adabor"           : (23.750, 90.340, 23.773, 90.360),
    "Rayer Bazar"      : (23.738, 90.352, 23.758, 90.368),
    "Hazaribagh"       : (23.720, 90.355, 23.745, 90.375),
    "Kamrangirchar"    : (23.698, 90.355, 23.722, 90.380),

    # ── Central ────────────────────────────────────────
    "Dhanmondi"        : (23.740, 90.365, 23.770, 90.390),
    "Kalabagan"        : (23.748, 90.378, 23.765, 90.393),
    "Panthapath"       : (23.748, 90.385, 23.762, 90.400),
    "Farmgate"         : (23.755, 90.385, 23.772, 90.400),
    "Karwan Bazar"     : (23.748, 90.393, 23.762, 90.408),
    "Shahbagh"         : (23.737, 90.390, 23.752, 90.405),
    "Elephant Road"    : (23.733, 90.383, 23.748, 90.398),
    "Eskaton"          : (23.745, 90.400, 23.760, 90.415),
    "Hatirpool"        : (23.738, 90.378, 23.752, 90.392),
    "New Market"       : (23.730, 90.378, 23.745, 90.392),

    # ── Northeast ──────────────────────────────────────
    "Gulshan"          : (23.775, 90.405, 23.812, 90.438),
    "Banani"           : (23.788, 90.395, 23.810, 90.418),
    "Baridhara"        : (23.790, 90.425, 23.820, 90.455),
    "Niketan"          : (23.770, 90.408, 23.790, 90.425),
    "Badda"            : (23.770, 90.430, 23.802, 90.462),
    "Aftabnagar"       : (23.755, 90.438, 23.778, 90.460),
    "Vatara"           : (23.800, 90.445, 23.830, 90.470),
    "Bashabo"          : (23.740, 90.432, 23.763, 90.452),

    # ── East ───────────────────────────────────────────
    "Rampura"          : (23.755, 90.418, 23.778, 90.440),
    "Malibagh"         : (23.745, 90.413, 23.762, 90.432),
    "Mughda"           : (23.738, 90.422, 23.758, 90.442),
    "Khilgaon"         : (23.730, 90.428, 23.755, 90.452),
    "Goran"            : (23.720, 90.428, 23.742, 90.450),
    "Demra"            : (23.695, 90.445, 23.725, 90.475),

    # ── Southeast ──────────────────────────────────────
    "Tejgaon"          : (23.755, 90.395, 23.780, 90.415),
    "Tejgaon Ind."     : (23.762, 90.405, 23.782, 90.422),
    "Motijheel"        : (23.720, 90.415, 23.745, 90.435),
    "Dilkusha"         : (23.723, 90.415, 23.737, 90.428),
    "Khilgaon"         : (23.730, 90.428, 23.755, 90.452),
    "Jatrabari"        : (23.700, 90.422, 23.724, 90.445),
    "Postogola"        : (23.690, 90.415, 23.710, 90.438),

    # ── South/Old Dhaka ────────────────────────────────
    "Old Dhaka"        : (23.695, 90.390, 23.725, 90.425),
    "Lalbagh"          : (23.710, 90.372, 23.730, 90.398),
    "Wari"             : (23.710, 90.413, 23.728, 90.432),
    "Sutrapur"         : (23.705, 90.405, 23.722, 90.425),
    "Chawkbazar"       : (23.713, 90.388, 23.730, 90.405),
    "Kotwali"          : (23.700, 90.400, 23.718, 90.418),
    "Dholaikhal"       : (23.718, 90.408, 23.732, 90.422),
}

def classify_area(lat, lon):
    """Returns the area name if coordinates fall inside a known bounding box."""
    if lat is None or lon is None:
        return "Unknown"
    for area, (min_lat, min_lon, max_lat, max_lon) in AREA_BOXES.items():
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return area
    return "Other Dhaka"


# ── STEP 3: Parse elements ─────────────────────────────────────────────────────
restaurants = []

for element in data["elements"]:
    if "tags" not in element:
        continue

    tags = element["tags"]
    amenity_type = tags.get("amenity", "")
    if amenity_type not in ["restaurant", "cafe", "fast_food", "food_court"]:
        continue

    # Get name — skip truly unnamed places
    name = tags.get("name", "").strip()
    if not name:
        continue

    # Build address
    address_parts = []
    if tags.get("addr:housenumber"):
        address_parts.append(tags["addr:housenumber"])
    if tags.get("addr:street"):
        address_parts.append(tags["addr:street"])
    if tags.get("addr:suburb"):
        address_parts.append(tags["addr:suburb"])
    if tags.get("addr:full"):
        address_parts = [tags["addr:full"]]
    address = ", ".join(address_parts) if address_parts else "N/A"

    # Get coordinates
    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None and "center" in element:
        lat = element["center"].get("lat")
        lon = element["center"].get("lon")

    # Get rating if available (some OSM entries have it)
    try:
        rating = float(tags.get("stars") or tags.get("rating") or 0)
    except:
        rating = 0.0

    restaurants.append({
        "Name"          : name,
        "Type"          : amenity_type.replace("_", " ").title(),
        "Cuisine"       : tags.get("cuisine", "N/A"),
        "Area"          : classify_area(lat, lon),
        "Address"       : address,
        "Phone"         : tags.get("phone") or tags.get("contact:phone", "N/A"),
        "Website"       : tags.get("website") or tags.get("contact:website", "N/A"),
        "Opening Hours" : tags.get("opening_hours", "N/A"),
        "OSM Rating"    : rating if rating > 0 else "N/A",
        "Latitude"      : lat,
        "Longitude"     : lon,
        "Google Maps"   : f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "N/A",
    })


# ── STEP 4: Clean & deduplicate ────────────────────────────────────────────────
df = pd.DataFrame(restaurants)
before = len(df)

# Remove duplicates
df.drop_duplicates(subset=["Name", "Address"], inplace=True)

# Remove suspiciously short names (e.g. "A", "1")
df = df[df["Name"].str.len() > 2]

# Sort: rated ones first (descending), unrated at bottom
df["_sort_rating"] = pd.to_numeric(df["OSM Rating"], errors="coerce").fillna(-1)
df.sort_values("_sort_rating", ascending=False, inplace=True)
df.drop(columns=["_sort_rating"], inplace=True)
df.reset_index(drop=True, inplace=True)

after = len(df)


# ── STEP 5: Save main files ────────────────────────────────────────────────────
df.to_csv("dhaka_restaurants.csv", index=False, encoding="utf-8-sig")
# ── Save weekly snapshot for trend analysis ────────────────────────────────────
import datetime
snapshot_dir = "data/snapshots"
os.makedirs(snapshot_dir, exist_ok=True)
today = datetime.date.today().strftime("%Y-%m-%d")
snapshot_path = f"{snapshot_dir}/{today}.csv"
df.to_csv(snapshot_path, index=False, encoding="utf-8-sig")
print(f"  -> Snapshot saved: {snapshot_path}")
# Save Excel with multiple sheets
with pd.ExcelWriter("dhaka_restaurants.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="All Places", index=False)

    # Sheet per type
    for place_type in df["Type"].unique():
        sheet_df = df[df["Type"] == place_type]
        sheet_name = place_type[:31]  # Excel sheet name max 31 chars
        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Sheet per area
    area_summary = df.groupby("Area").agg(
        Total=("Name", "count"),
        Restaurants=("Type", lambda x: (x == "Restaurant").sum()),
        Cafes=("Type", lambda x: (x == "Cafe").sum()),
        Fast_Food=("Type", lambda x: (x == "Fast Food").sum()),
    ).sort_values("Total", ascending=False).reset_index()
    area_summary.to_excel(writer, sheet_name="Area Summary", index=False)

    # Cuisine breakdown sheet
    cuisine_counts = df[df["Cuisine"] != "N/A"]["Cuisine"].value_counts().reset_index()
    cuisine_counts.columns = ["Cuisine", "Count"]
    cuisine_counts.to_excel(writer, sheet_name="Cuisine Breakdown", index=False)


# ── STEP 6: Generate statistics & charts ──────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend (works without a display)
    import matplotlib.pyplot as plt

    os.makedirs("charts", exist_ok=True)

    # Chart 1: Type breakdown (pie)
    type_counts = df["Type"].value_counts()
    plt.figure(figsize=(7, 7))
    plt.pie(type_counts.values, labels=type_counts.index, autopct="%1.1f%%",
            colors=["#FF6B6B", "#4ECDC4", "#FFE66D", "#A8DADC"])
    plt.title("Dhaka Food Places — Type Breakdown", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("charts/type_breakdown.png", dpi=150)
    plt.close()

    # Chart 2: Top 10 areas (bar)
    top_areas = df["Area"].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    bars = plt.barh(top_areas.index[::-1], top_areas.values[::-1], color="#FF6B6B")
    plt.xlabel("Number of Places")
    plt.title("Top 10 Areas by Number of Food Places", fontsize=14, fontweight="bold")
    for bar, val in zip(bars, top_areas.values[::-1]):
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                 str(val), va="center", fontsize=10)
    plt.tight_layout()
    plt.savefig("charts/top_areas.png", dpi=150)
    plt.close()

    # Chart 3: Top 10 cuisines (bar)
    top_cuisines = df[df["Cuisine"] != "N/A"]["Cuisine"].value_counts().head(10)
    if not top_cuisines.empty:
        plt.figure(figsize=(10, 6))
        bars = plt.barh(top_cuisines.index[::-1], top_cuisines.values[::-1], color="#4ECDC4")
        plt.xlabel("Number of Places")
        plt.title("Top 10 Cuisines in Dhaka", fontsize=14, fontweight="bold")
        for bar, val in zip(bars, top_cuisines.values[::-1]):
            plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                     str(val), va="center", fontsize=10)
        plt.tight_layout()
        plt.savefig("charts/top_cuisines.png", dpi=150)
        plt.close()

    charts_saved = True

except ImportError:
    charts_saved = False


# ── STEP 7: Summary ────────────────────────────────────────────────────────────
print("=" * 50)
print("  DONE! Summary")
print("=" * 50)
print(f"  Raw entries fetched    : {before}")
print(f"  After cleaning         : {after}")
print(f"  Removed (duplicates)   : {before - after}")
print()
print(f"  Restaurants            : {len(df[df['Type'] == 'Restaurant'])}")
print(f"  Cafes                  : {len(df[df['Type'] == 'Cafe'])}")
print(f"  Fast Food              : {len(df[df['Type'] == 'Fast Food'])}")
print()
print("  Top 5 Areas:")
for area, count in df["Area"].value_counts().head(5).items():
    print(f"    {area:<20} {count} places")
print("=" * 50)
print()
print("  Files saved:")
print("  -> dhaka_restaurants.csv")
print("  -> dhaka_restaurants.xlsx  (5 sheets inside)")
if charts_saved:
    print("  -> charts/type_breakdown.png")
    print("  -> charts/top_areas.png")
    print("  -> charts/top_cuisines.png")
else:
    print("  (charts skipped — matplotlib not installed)")
print()
print("Open dhaka_restaurants.xlsx in Excel to explore!")