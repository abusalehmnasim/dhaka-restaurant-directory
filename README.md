# 🍽️ Dhaka Restaurant Directory

A Python data collection and analysis project that compiles **2,000+ food places** across Dhaka city using free, open-source data — no paid API required.

## 🌐 Live Demo
👉 [View the Live Dashboard](https://dhaka-restaurant-directory-dulhlwyc5cbjwfxkympn6q.streamlit.app)

## 📌 What This Project Does

- Fetches live restaurant data from OpenStreetMap via the Overpass API
- Cleans and deduplicates 2,000+ entries automatically
- Classifies places into 42 named areas/thanas of Dhaka
- Generates statistical charts (type breakdown, top areas, top cuisines)
- Exports data to multi-sheet Excel and CSV with clickable Google Maps links
- Builds an interactive web dashboard with live filters, charts, heatmap, and pin map
- Finds the nearest restaurants to any GPS location using the Haversine formula
- Includes a Telegram bot for real-time restaurant search
- Automated weekly data pipeline via GitHub Actions (CI/CD)

## 📊 Stats

| Metric | Value |
|---|---|
| Total places | 2,000+ |
| Named areas | 42 |
| Duplicates removed | 183 |
| Map pins | 1,900+ |
| Auto-update | Every Monday |

## 🗂️ Project Structure
```
dhaka-restaurants/
├── main.py           # Data collection, cleaning, classification, export
├── search.py         # Interactive CLI search tool
├── map.py            # Interactive HTML map generator
├── dashboard.py      # Streamlit web dashboard
├── bot.py            # Telegram bot
├── requirements.txt  # Python dependencies
├── charts/           # Auto-generated PNG charts
├── dhaka_restaurants.csv
└── dhaka_restaurants.xlsx
```

## 🛠️ Tech Stack

- **Python 3.x**
- **Requests** — HTTP data fetching
- **Pandas** — data cleaning and analysis
- **Matplotlib** — chart generation
- **Folium** — interactive map generation
- **Streamlit + Plotly** — web dashboard
- **python-telegram-bot** — Telegram bot
- **GitHub Actions** — automated weekly data pipeline
- **OpenStreetMap + Overpass API** — free data source

## 🚀 How to Run
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect and process data
python main.py

# 3. Launch the web dashboard
streamlit run dashboard.py

# 4. Search the data via CLI
python search.py

# 5. Generate the interactive HTML map
python map.py

# 6. Run the Telegram bot (requires VPN in Bangladesh)
python bot.py
```

## ✨ Features

### Web Dashboard
- Live filters by type, area, cuisine, and name
- Interactive bar and pie charts
- Pin map and heatmap in tabs
- Nearest restaurant finder using GPS coordinates
- Download filtered results as CSV

### Telegram Bot
- Search by area, cuisine, or name
- View statistics
- Get Google Maps links for each result

### Auto-Update Pipeline
- GitHub Actions runs every Monday
- Fetches fresh data from OpenStreetMap
- Commits updated CSV, Excel, and map back to repo automatically

## 📄 Data Source

[OpenStreetMap](https://www.openstreetmap.org/) via [Overpass API](https://overpass-api.de/) — open data, free to use.

## 👤 Author

**Abu Saleh M Nasim** — BBA (Finance), Bangladesh University of Professionals  
GitHub: [@abusalehmnasim](https://github.com/abusalehmnasim)