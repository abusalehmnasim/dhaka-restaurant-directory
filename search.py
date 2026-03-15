import pandas as pd
import os

# ── Load data ──────────────────────────────────────────────────────────────────
CSV_FILE = "dhaka_restaurants.csv"

if not os.path.exists(CSV_FILE):
    print("ERROR: dhaka_restaurants.csv not found.")
    print("Please run main.py first to collect the data.")
    exit()

df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
# Fill text columns with "N/A", leave numeric columns as-is
text_cols = df.select_dtypes(include="str").columns
df[text_cols] = df[text_cols].fillna("N/A")

# ── Helper functions ───────────────────────────────────────────────────────────
def display_results(results, query_label):
    """Neatly prints a dataframe of results."""
    if results.empty:
        print(f"\n  No results found for: '{query_label}'")
        print("  Try a different keyword.\n")
        return

    print(f"\n  Found {len(results)} result(s) for '{query_label}':\n")
    print(f"  {'#':<5} {'Name':<35} {'Type':<12} {'Area':<18} {'Cuisine':<20} {'Phone'}")
    print("  " + "-" * 105)

    for i, (_, row) in enumerate(results.iterrows(), 1):
        name    = str(row["Name"])[:33]
        rtype   = str(row["Type"])[:10]
        area    = str(row["Area"])[:16]
        cuisine = str(row["Cuisine"])[:18]
        phone   = str(row["Phone"])[:20]
        print(f"  {i:<5} {name:<35} {rtype:<12} {area:<18} {cuisine:<20} {phone}")

    print()


def search_by_area(area_query):
    """Search restaurants by area name (partial match, case-insensitive)."""
    results = df[df["Area"].str.contains(area_query, case=False, na=False)]
    display_results(results, area_query)


def search_by_cuisine(cuisine_query):
    """Search restaurants by cuisine type (partial match, case-insensitive)."""
    results = df[df["Cuisine"].str.contains(cuisine_query, case=False, na=False)]
    display_results(results, cuisine_query)


def search_by_name(name_query):
    """Search restaurants by name (partial match, case-insensitive)."""
    results = df[df["Name"].str.contains(name_query, case=False, na=False)]
    display_results(results, name_query)


def show_all_areas():
    """List all available areas with counts."""
    print("\n  Available Areas:")
    print("  " + "-" * 35)
    area_counts = df["Area"].value_counts()
    for area, count in area_counts.items():
        print(f"  {area:<25} {count} places")
    print()


def show_all_cuisines():
    """List all available cuisines with counts."""
    cuisines = df[df["Cuisine"] != "N/A"]["Cuisine"].value_counts()
    print("\n  Available Cuisines:")
    print("  " + "-" * 35)
    for cuisine, count in cuisines.items():
        print(f"  {cuisine:<25} {count} places")
    print()


def export_results(results, filename):
    """Export filtered results to a new Excel file."""
    if results.empty:
        print("  Nothing to export.\n")
        return
    filepath = f"{filename}.xlsx"
    results.to_excel(filepath, index=False)
    print(f"  Exported {len(results)} rows to '{filepath}'\n")


# ── Main menu loop ─────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 50)
    print("  Dhaka Restaurant Search Tool")
    print(f"  {len(df)} places loaded")
    print("=" * 50)

    last_results = pd.DataFrame()  # stores last search for export

    while True:
        print("\n  What do you want to do?")
        print("  [1] Search by Area        (e.g. Gulshan, Mirpur)")
        print("  [2] Search by Cuisine     (e.g. Bengali, Chinese)")
        print("  [3] Search by Name        (e.g. KFC, Pizza)")
        print("  [4] List all Areas")
        print("  [5] List all Cuisines")
        print("  [6] Export last search to Excel")
        print("  [0] Exit")

        choice = input("\n  Enter choice (0-6): ").strip()

        if choice == "1":
            area = input("  Enter area name: ").strip()
            if area:
                last_results = df[df["Area"].str.contains(area, case=False, na=False)]
                display_results(last_results, area)

        elif choice == "2":
            cuisine = input("  Enter cuisine type: ").strip()
            if cuisine:
                last_results = df[df["Cuisine"].str.contains(cuisine, case=False, na=False)]
                display_results(last_results, cuisine)

        elif choice == "3":
            name = input("  Enter restaurant name: ").strip()
            if name:
                last_results = df[df["Name"].str.contains(name, case=False, na=False)]
                display_results(last_results, name)

        elif choice == "4":
            show_all_areas()

        elif choice == "5":
            show_all_cuisines()

        elif choice == "6":
            if last_results.empty:
                print("\n  No search has been done yet. Search first, then export.\n")
            else:
                filename = input("  Enter filename (without .xlsx): ").strip()
                if filename:
                    export_results(last_results, filename)

        elif choice == "0":
            print("\n  Goodbye!\n")
            break

        else:
            print("\n  Invalid choice. Enter a number between 0 and 6.\n")


if __name__ == "__main__":
    main()