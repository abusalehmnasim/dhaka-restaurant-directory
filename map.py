import pandas as pd
import folium
from folium.plugins import MarkerCluster, Search
import os

print("Loading data...")

df = pd.read_csv("dhaka_restaurants.csv", encoding="utf-8-sig")

# Keep only rows that have coordinates
df = df.dropna(subset=["Latitude", "Longitude"])
print(f"  {len(df)} places with coordinates found\n")

# ── Color coding by type ───────────────────────────────────────────────────────
COLOR_MAP = {
    "Restaurant" : "red",
    "Cafe"       : "blue",
    "Fast Food"  : "orange",
    "Food Court" : "purple",
}

ICON_MAP = {
    "Restaurant" : "cutlery",
    "Cafe"       : "coffee",
    "Fast Food"  : "fire",
    "Food Court" : "star",
}

# ── Build the map ──────────────────────────────────────────────────────────────
print("Building map...")

# Center on Dhaka
dhaka_map = folium.Map(
    location=[23.780, 90.399],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# Add a marker cluster (groups pins when zoomed out)
marker_cluster = MarkerCluster(
    name="All Places",
    overlay=True,
    control=True,
    disableClusteringAtZoom=16
).add_to(dhaka_map)

# ── Add pins ───────────────────────────────────────────────────────────────────
for _, row in df.iterrows():
    place_type = str(row.get("Type", "Restaurant"))
    color      = COLOR_MAP.get(place_type, "gray")
    icon_name  = ICON_MAP.get(place_type, "info-sign")

    # Build popup content
    name     = str(row.get("Name", "Unknown"))
    cuisine  = str(row.get("Cuisine", "N/A"))
    area     = str(row.get("Area", "N/A"))
    address  = str(row.get("Address", "N/A"))
    phone    = str(row.get("Phone", "N/A"))
    hours    = str(row.get("Opening Hours", "N/A"))

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 200px;">
        <h4 style="margin:0 0 6px 0; color:#c0392b;">{name}</h4>
        <table style="font-size:13px; border-collapse:collapse; width:100%">
            <tr><td style="color:#888; padding:2px 8px 2px 0">Type</td>
                <td><b>{place_type}</b></td></tr>
            <tr><td style="color:#888; padding:2px 8px 2px 0">Cuisine</td>
                <td>{cuisine}</td></tr>
            <tr><td style="color:#888; padding:2px 8px 2px 0">Area</td>
                <td>{area}</td></tr>
            <tr><td style="color:#888; padding:2px 8px 2px 0">Address</td>
                <td>{address}</td></tr>
            <tr><td style="color:#888; padding:2px 8px 2px 0">Phone</td>
                <td>{phone}</td></tr>
            <tr><td style="color:#888; padding:2px 8px 2px 0">Hours</td>
                <td>{hours}</td></tr>
        </table>
    </div>
    """

    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=name,
        icon=folium.Icon(color=color, icon=icon_name, prefix="glyphicon")
    ).add_to(marker_cluster)


# ── Legend ─────────────────────────────────────────────────────────────────────
legend_html = """
<div style="
    position: fixed;
    bottom: 40px; right: 20px;
    background: white;
    border: 2px solid #ccc;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: Arial, sans-serif;
    font-size: 13px;
    z-index: 9999;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
">
    <b style="font-size:14px;">Dhaka Food Places</b><br><br>
    <span style="color:#c0392b;">&#9679;</span> Restaurant<br>
    <span style="color:#2980b9;">&#9679;</span> Cafe<br>
    <span style="color:#e67e22;">&#9679;</span> Fast Food<br>
    <span style="color:#8e44ad;">&#9679;</span> Food Court<br>
    <br>
    <span style="color:#555; font-size:12px;">Click any pin for details</span>
</div>
"""
dhaka_map.get_root().html.add_child(folium.Element(legend_html))


# ── Title ──────────────────────────────────────────────────────────────────────
title_html = """
<div style="
    position: fixed;
    top: 12px; left: 50%; transform: translateX(-50%);
    background: white;
    border: 2px solid #ccc;
    border-radius: 8px;
    padding: 8px 20px;
    font-family: Arial, sans-serif;
    font-size: 16px;
    font-weight: bold;
    z-index: 9999;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
">
    🍽️ Dhaka Restaurant Map
</div>
"""
dhaka_map.get_root().html.add_child(folium.Element(title_html))


# ── Save ───────────────────────────────────────────────────────────────────────
output_file = "dhaka_restaurants_map.html"
dhaka_map.save(output_file)

print("=" * 45)
print("  Map built successfully!")
print("=" * 45)
print(f"  Total pins placed  : {len(df)}")
print(f"  File saved         : {output_file}")
print()
print("  Open 'dhaka_restaurants_map.html'")
print("  in any browser to explore the map!")