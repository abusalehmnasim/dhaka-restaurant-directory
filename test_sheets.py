import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Dhaka Restaurant Ratings").sheet1
    print("✅ Sheet connected:", sheet.title)
except Exception as e:
    print("❌ Error:", e)