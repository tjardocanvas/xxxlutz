import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
import os

# === Laad credentials vanuit GitHub Secret ===
google_creds = json.loads(os.environ["GOOGLE_SHEETS_CREDS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)

# === Open de sheet ===
sheet = client.open("XXXLutz Orders").sheet1  # Moet overeenkomen met je echte sheetnaam

# === Mirakl API setup ===
api_url = "https://marketplace.xxxlgroup.mirakl.net/api/orders"  # Vervang xxx met jouw Mirakl-URL
headers = {
    "Authorization": f'Bearer {os.environ["MIRAKL_API_KEY"]}'
}

response = requests.get(api_url, headers=headers)
orders = response.json().get("orders", [])

# === Sheet vullen ===
sheet.clear()
sheet.append_row(["Order ID", "Klantnaam", "Product", "Aantal", "Prijs"])

for order in orders:
    for line in order["order_lines"]:
        sheet.append_row([
            order["id"],
            f'{order["customer"]["firstname"]} {order["customer"]["lastname"]}',
            line["product_title"],
            line["quantity"],
            line["price"]
        ])
