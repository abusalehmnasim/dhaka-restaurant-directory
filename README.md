## 🌐 Live Demo
👉 [View the Live Dashboard](https://dhaka-restaurant-directory-dulhlwyc5cbjwfxkympn6q.streamlit.app)

# 🍽️ Dhaka Restaurant Directory

A Python data collection and analysis project that compiles **2,000+ food places** across Dhaka city using free, open-source data — no paid API required.

## 📌 What This Project Does

- Fetches live restaurant data from OpenStreetMap via the Overpass API
- Cleans and deduplicates 2,000+ entries automatically
- Classifies places into 40+ named areas/thanas of Dhaka
- Generates statistical charts (type breakdown, top areas, top cuisines)
- Exports data to multi-sheet Excel and CSV
- Builds an interactive HTML map with clickable pins for every location
- Includes a command-line search tool (search by area, cuisine, or name)

## 🗂️ Project Structure
```
dhaka-restaurants/
├── main.py          # Data collection, cleaning, classification, export
├── search.py        # Interactive CLI search tool
├── map.py           # Interactive HTML map generator
├── charts/          # Auto-generated PNG charts
├── dhaka_restaurants.csv
└── dhaka_restaurants.xlsx
```

## 🛠️ Tech Stack

- Python 3.x
- Requests — HTTP data fetching
- Pandas — data cleaning and analysis
- Matplotlib — chart generation
- Folium — interactive map generation
- OpenStreetMap + Overpass API — free data source

## 🚀 How to Run
```bash
# 1. Install dependencies
pip install requests pandas openpyxl matplotlib folium

# 2. Collect and process data
python main.py

# 3. Search the data interactively
python search.py

# 4. Generate the interactive map
python map.py
```

## 📊 Sample Output

- **2,021** food places collected
- **42** named areas classified
- **182** duplicates removed
- **1,901** pins on interactive map

## 📄 Data Source

[OpenStreetMap](https://www.openstreetmap.org/) via [Overpass API](https://overpass-api.de/) — open data, free to use.