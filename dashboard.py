import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import os
import math

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

all_types = ["All"] + sorted(df["Type"].unique().tolist())
selected_type = st.sidebar.selectbox("Type", all_types)

all_areas = ["All"] + sorted(df["Area"].unique().tolist())
selected_area = st.sidebar.selectbox("Area", all_areas)

all_cuisines = ["All"] + sorted(df[df["Cuisine"] != "N/A"]["Cuisine"].unique().tolist())
selected_cuisine = st.sidebar.selectbox("Cuisine", all_cuisines)

name_search = st.sidebar.text_input("Search by Name", "")

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
    st_folium(m, width=None, height=500, key="main_map")
    if len(filtered.dropna(subset=["Latitude", "Longitude"])) > 500:
        st.caption("⚠️ Showing first 500 pins for performance. Use filters to narrow down.")

with heatmap_tab:
    m2 = folium.Map(location=[23.780, 90.399], zoom_start=12)
    heat_data = filtered.dropna(subset=["Latitude", "Longitude"])[["Latitude", "Longitude"]].values.tolist()
    HeatMap(heat_data, radius=10, blur=8).add_to(m2)
    st_folium(m2, width=None, height=500, key="heat_map")

st.divider()

# ── Data table ─────────────────────────────────────────────────────────────────
st.subheader("📋 Data Table")

show_cols = ["Name", "Type", "Cuisine", "Area", "Address", "Phone", "Opening Hours", "Google Maps"]
available_cols = [c for c in show_cols if c in filtered.columns]
st.dataframe(filtered[available_cols], use_container_width=True, height=400)

csv = filtered.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="⬇️ Download filtered results as CSV",
    data=csv,
    file_name="filtered_restaurants.csv",
    mime="text/csv",
    key="download_filtered"
)

st.caption("Data source: OpenStreetMap via Overpass API | Updated weekly via GitHub Actions")

st.divider()

# ── Nearest Restaurant Finder ──────────────────────────────────────────────────
st.subheader("📍 Nearest Restaurant Finder")
st.markdown("Enter your location coordinates to find the closest restaurants.")

col_lat, col_lon = st.columns(2)
with col_lat:
    user_lat = st.number_input("Your Latitude", value=23.780, format="%.6f", step=0.001)
with col_lon:
    user_lon = st.number_input("Your Longitude", value=90.399, format="%.6f", step=0.001)

near_col1, near_col2 = st.columns(2)
with near_col1:
    top_n = st.slider("How many results?", min_value=5, max_value=30, value=10)
with near_col2:
    filter_type_near = st.selectbox("Filter by type", ["All"] + sorted(df["Type"].unique().tolist()), key="near_type")

if st.button("🔍 Find Nearest Restaurants"):
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    near_df = df.dropna(subset=["Latitude", "Longitude"]).copy()
    if filter_type_near != "All":
        near_df = near_df[near_df["Type"] == filter_type_near]

    near_df["Distance (km)"] = near_df.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]),
        axis=1
    )

    nearest = near_df.nsmallest(top_n, "Distance (km)").reset_index(drop=True)
    nearest["Distance (km)"] = nearest["Distance (km)"].round(3)
    nearest.index += 1

    st.session_state["nearest"] = nearest
    st.session_state["nearest_lat"] = user_lat
    st.session_state["nearest_lon"] = user_lon

if "nearest" in st.session_state:
    nearest = st.session_state["nearest"]
    user_lat_s = st.session_state["nearest_lat"]
    user_lon_s = st.session_state["nearest_lon"]

    st.success(f"✅ Found {len(nearest)} nearest places to ({user_lat_s}, {user_lon_s})")

    show_cols_n = ["Name", "Type", "Cuisine", "Area", "Address", "Phone", "Distance (km)", "Google Maps"]
    available_n = [c for c in show_cols_n if c in nearest.columns]
    st.dataframe(nearest[available_n], use_container_width=True)

    st.markdown("**📍 Map of nearest restaurants:**")
    near_map = folium.Map(location=[user_lat_s, user_lon_s], zoom_start=14)

    folium.Marker(
        location=[user_lat_s, user_lon_s],
        popup="📍 Your Location",
        tooltip="You are here",
        icon=folium.Icon(color="green", icon="user", prefix="glyphicon")
    ).add_to(near_map)

    for _, row in nearest.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(
                f"<b>{row['Name']}</b><br>{row['Type']}<br>{row['Distance (km)']} km away",
                max_width=200
            ),
            tooltip=f"{row['Name']} ({row['Distance (km)']} km)",
            icon=folium.Icon(
                color=COLOR_MAP.get(str(row["Type"]), "gray"),
                icon="cutlery",
                prefix="glyphicon"
            )
        ).add_to(near_map)

    st_folium(near_map, width=None, height=450, key="nearest_map")

    csv_near = nearest.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="⬇️ Download nearest results as CSV",
        data=csv_near,
        file_name="nearest_restaurants.csv",
        mime="text/csv",
        key="download_nearest"
    )
    st.divider()

# ── Trend Analysis ─────────────────────────────────────────────────────────────
st.subheader("📈 Trend Analysis")

snapshot_dir = "data/snapshots"

if not os.path.exists(snapshot_dir):
    st.info("📅 Trend data not available yet. Run main.py weekly to build historical data.")
else:
    snapshot_files = sorted([
        f for f in os.listdir(snapshot_dir)
        if f.endswith(".csv")
    ])

    if len(snapshot_files) < 2:
        st.info(f"📅 Only {len(snapshot_files)} snapshot(s) collected so far. Come back next week for trend charts! First snapshot: {snapshot_files[0] if snapshot_files else 'none'}")
    else:
        # Load all snapshots
        records = []
        for fname in snapshot_files:
            date_str = fname.replace(".csv", "")
            try:
                snap_df = pd.read_csv(
                    os.path.join(snapshot_dir, fname),
                    encoding="utf-8-sig"
                )
                text_cols = snap_df.select_dtypes(include="object").columns
                snap_df[text_cols] = snap_df[text_cols].fillna("N/A")
                records.append({
                    "date"        : date_str,
                    "total"       : len(snap_df),
                    "restaurants" : len(snap_df[snap_df["Type"] == "Restaurant"]),
                    "cafes"       : len(snap_df[snap_df["Type"] == "Cafe"]),
                    "fast_food"   : len(snap_df[snap_df["Type"] == "Fast Food"]),
                    "snap_df"     : snap_df
                })
            except Exception:
                continue

        trend_df = pd.DataFrame([{k: v for k, v in r.items() if k != "snap_df"} for r in records])
        trend_df["date"] = pd.to_datetime(trend_df["date"])
        trend_df = trend_df.sort_values("date")
        trend_df["weekly_change"] = trend_df["total"].diff().fillna(0).astype(int)

        # ── Chart 1: Total places over time ───────────────────────────────────
        st.markdown("### 🏙️ Total Food Places Over Time")
        fig_trend = px.line(
            trend_df, x="date", y="total",
            markers=True,
            labels={"date": "Date", "total": "Total Places"},
            color_discrete_sequence=["#FF6B6B"]
        )
        fig_trend.update_traces(line_width=3, marker_size=8)
        fig_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Chart 2: Type breakdown over time ─────────────────────────────────
        st.markdown("### 🍽️ Type Breakdown Over Time")
        type_trend = trend_df[["date", "restaurants", "cafes", "fast_food"]].melt(
            id_vars="date",
            var_name="Type",
            value_name="Count"
        )
        type_trend["Type"] = type_trend["Type"].map({
            "restaurants": "Restaurant",
            "cafes": "Cafe",
            "fast_food": "Fast Food"
        })
        fig_type = px.line(
            type_trend, x="date", y="Count",
            color="Type", markers=True,
            color_discrete_map={
                "Restaurant": "#FF6B6B",
                "Cafe": "#4ECDC4",
                "Fast Food": "#FFE66D"
            }
        )
        fig_type.update_traces(line_width=2, marker_size=6)
        st.plotly_chart(fig_type, use_container_width=True)

        # ── Chart 3: Area growth ───────────────────────────────────────────────
        st.markdown("### 📍 Area Growth (First vs Latest Snapshot)")
        first_snap = records[0]["snap_df"]
        last_snap  = records[-1]["snap_df"]

        first_areas = first_snap["Area"].value_counts().rename("first")
        last_areas  = last_snap["Area"].value_counts().rename("latest")

        area_growth = pd.concat([first_areas, last_areas], axis=1).fillna(0)
        area_growth["change"] = (area_growth["latest"] - area_growth["first"]).astype(int)
        area_growth = area_growth[area_growth["change"] != 0].sort_values("change", ascending=False)

        if area_growth.empty:
            st.info("No area changes detected yet between snapshots.")
        else:
            fig_growth = px.bar(
                area_growth.reset_index(),
                x="index", y="change",
                color="change",
                color_continuous_scale="RdYlGn",
                labels={"index": "Area", "change": "Change in Places"},
            )
            fig_growth.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_growth, use_container_width=True)

        # ── Weekly change table ────────────────────────────────────────────────
        st.markdown("### 📋 Weekly Snapshot Summary")
        summary = trend_df[["date", "total", "restaurants", "cafes", "fast_food", "weekly_change"]].copy()
        summary["date"] = summary["date"].dt.strftime("%Y-%m-%d")
        summary.columns = ["Date", "Total", "Restaurants", "Cafes", "Fast Food", "Weekly Change"]
        st.dataframe(summary, use_container_width=True)
        st.divider()

# ── User Ratings System ────────────────────────────────────────────────────────
st.subheader("⭐ Rate a Restaurant")

import gspread
from google.oauth2.service_account import Credentials
import json

# Load credentials
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Dhaka Restaurant Ratings").sheet1
        return sheet
    except Exception as e:
        return None

sheet = get_sheet()

if sheet is None:
    st.warning("⚠️ Ratings system unavailable — credentials not found.")
else:
    tab_rate, tab_view = st.tabs(["✍️ Submit a Rating", "📊 View All Ratings"])

    with tab_rate:
        st.markdown("Found a restaurant in our directory? Rate it!")

        # Restaurant name input with autocomplete from dataset
        all_names = sorted(df["Name"].unique().tolist())
        selected_restaurant = st.selectbox("Select Restaurant", all_names, key="rate_restaurant")

        # Show restaurant details
        resto_info = df[df["Name"] == selected_restaurant].iloc[0]
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"**Type:** {resto_info['Type']}")
            st.markdown(f"**Area:** {resto_info['Area']}")
        with col_info2:
            st.markdown(f"**Cuisine:** {resto_info['Cuisine']}")
            st.markdown(f"**Address:** {resto_info['Address']}")

        # Rating input
        rating = st.slider("Your Rating", min_value=1, max_value=5, value=3, key="rating_slider")
        stars = "⭐" * rating
        st.markdown(f"Your rating: {stars}")

        # Comment input
        comment = st.text_area("Your Comment (optional)", placeholder="How was the food? Service? Ambiance?", key="rating_comment")

        if st.button("Submit Rating", key="submit_rating"):
            if not comment:
                comment = "No comment"
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            try:
                sheet.append_row([
                    selected_restaurant,
                    str(resto_info["Type"]),
                    str(resto_info["Area"]),
                    rating,
                    comment,
                    timestamp
                ])
                st.success(f"✅ Thank you! Your {rating}-star rating for **{selected_restaurant}** has been saved.")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to save rating: {e}")

    with tab_view:
        st.markdown("### All Submitted Ratings")

        try:
            all_ratings = sheet.get_all_records()

            if not all_ratings:
                st.info("No ratings submitted yet. Be the first to rate a restaurant!")
            else:
                ratings_df = pd.DataFrame(all_ratings)
                ratings_df.columns = ["Restaurant", "Type", "Area", "Rating", "Comment", "Timestamp"]

                # Summary stats
                total_ratings = len(ratings_df)
                avg_rating = ratings_df["Rating"].mean()
                top_rated = ratings_df.groupby("Restaurant")["Rating"].mean().idxmax()

                r1, r2, r3 = st.columns(3)
                r1.metric("Total Ratings", total_ratings)
                r2.metric("Average Rating", f"{avg_rating:.1f} ⭐")
                r3.metric("Top Rated", top_rated)

                # Top rated restaurants chart
                avg_by_resto = (
                    ratings_df.groupby("Restaurant")["Rating"]
                    .agg(["mean", "count"])
                    .reset_index()
                )
                avg_by_resto.columns = ["Restaurant", "Avg Rating", "Count"]
                avg_by_resto = avg_by_resto[avg_by_resto["Count"] >= 1].sort_values("Avg Rating", ascending=False).head(10)

                if not avg_by_resto.empty:
                    st.markdown("### 🏆 Top Rated Restaurants")
                    fig_ratings = px.bar(
                        avg_by_resto,
                        x="Avg Rating", y="Restaurant",
                        orientation="h",
                        color="Avg Rating",
                        color_continuous_scale="Greens",
                        text="Count",
                        height=400
                    )
                    fig_ratings.update_layout(coloraxis_showscale=False)
                    st.plotly_chart(fig_ratings, use_container_width=True)

                # Full ratings table
                st.markdown("### 📋 All Reviews")
                st.dataframe(
                    ratings_df.sort_values("Timestamp", ascending=False),
                    use_container_width=True,
                    height=400
                )

        except Exception as e:
            st.error(f"Could not load ratings: {e}")