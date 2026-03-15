import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dhaka Restaurant Directory",
    page_icon="🍽️",
    layout="wide"
)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("dhaka_restaurants.csv", encoding="utf-8-sig")
    text_cols = df.select_dtypes(include="object").columns
    df[text_cols] = df[text_cols].fillna("N/A")
    return df

df = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

# Type filter
all_types = ["All"] + sorted(df["Type"].unique().tolist())
selected_type = st.sidebar.selectbox("Type", all_types)

# Area filter
all_areas = ["All"] + sorted(df["Area"].unique().tolist())
selected_area = st.sidebar.selectbox("Area", all_areas)

# Cuisine filter
all_cuisines = ["All"] + sorted(df[df["Cuisine"] != "N/A"]["Cuisine"].unique().tolist())
selected_cuisine = st.sidebar.selectbox("Cuisine", all_cuisines)

# Name search
name_search = st.sidebar.text_input("Search by Name", "")

# Apply filters
filtered = df.copy()
if selected_type != "All":
    filtered = filtered[filtered["Type"] == selected_type]
if selected_area != "All":
    filtered = filtered[filtered["Area"] == selected_area]
if selected_cuisine != "All":
    filtered = filtered[filtered["Cuisine"] == selected_cuisine]
if name_search:
    filtered = filtered[filtered["Name"].str.contains(name_search, case=False, na=False)]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🍽️ Dhaka Restaurant Directory")
st.markdown("Interactive dashboard of **2,000+ food places** across Dhaka city — built with OpenStreetMap data.")

# ── KPI cards ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Places", len(filtered), delta=f"{len(filtered) - len(df)} from filters" if len(filtered) != len(df) else None)
col2.metric("Restaurants", len(filtered[filtered["Type"] == "Restaurant"]))
col3.metric("Cafes", len(filtered[filtered["Type"] == "Cafe"]))
col4.metric("Fast Food", len(filtered[filtered["Type"] == "Fast Food"]))

st.divider()

# ── Charts row ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Places by Area")
    area_counts = filtered["Area"].value_counts().head(15).reset_index()
    area_counts.columns = ["Area", "Count"]
    fig_area = px.bar(
        area_counts, x="Count", y="Area",
        orientation="h", color="Count",
        color_continuous_scale="Reds",
        height=450
    )
    fig_area.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_area, use_container_width=True)

with col_right:
    st.subheader("🌍 Top Cuisines")
    cuisine_data = filtered[filtered["Cuisine"] != "N/A"]["Cuisine"].value_counts().head(12).reset_index()
    cuisine_data.columns = ["Cuisine", "Count"]
    fig_cuisine = px.pie(
        cuisine_data, values="Count", names="Cuisine",
        color_discrete_sequence=px.colors.qualitative.Set3,
        height=450
    )
    fig_cuisine.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_cuisine, use_container_width=True)

st.divider()

# ── Map ────────────────────────────────────────────────────────────────────────
st.subheader("🗺️ Map View")

map_tab, heatmap_tab = st.tabs(["📍 Pin Map", "🔥 Heatmap"])

COLOR_MAP = {
    "Restaurant": "red",
    "Cafe":       "blue",
    "Fast Food":  "orange",
    "Food Court": "purple",
}

with map_tab:
    m = folium.Map(location=[23.780, 90.399], zoom_start=12)
    map_data = filtered.dropna(subset=["Latitude", "Longitude"]).head(500)

    for _, row in map_data.iterrows():
        color = COLOR_MAP.get(str(row["Type"]), "gray")
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=5,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(f"<b>{row['Name']}</b><br>{row['Type']}<br>{row['Area']}", max_width=200),
            tooltip=row["Name"]
        ).add_to(m)

    st_folium(m, width=None, height=500)
    if len(filtered.dropna(subset=["Latitude", "Longitude"])) > 500:
        st.caption("⚠️ Showing first 500 pins for performance. Use filters to narrow down.")

with heatmap_tab:
    m2 = folium.Map(location=[23.780, 90.399], zoom_start=12)
    heat_data = filtered.dropna(subset=["Latitude", "Longitude"])[["Latitude", "Longitude"]].values.tolist()
    HeatMap(heat_data, radius=10, blur=8).add_to(m2)
    st_folium(m2, width=None, height=500)

st.divider()

# ── Data table ─────────────────────────────────────────────────────────────────
st.subheader("📋 Data Table")

show_cols = ["Name", "Type", "Cuisine", "Area", "Address", "Phone", "Opening Hours", "Google Maps"]
available_cols = [c for c in show_cols if c in filtered.columns]
st.dataframe(filtered[available_cols], use_container_width=True, height=400)

# Download button
csv = filtered.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="⬇️ Download filtered results as CSV",
    data=csv,
    file_name="filtered_restaurants.csv",
    mime="text/csv"
)

st.caption("Data source: OpenStreetMap via Overpass API | Updated weekly via GitHub Actions")