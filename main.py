import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
import os

# === Google Sheets authenticatie ===
google_creds = json.loads(os.environ["GOOGLE_SHEETS_CREDS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)

# === Open de Google Sheet ===
sheet = client.open("XXXLutz Orders").sheet1

# === Mirakl API-aanroep ===
api_url = "https://marketplace.xxxlgroup.com/api/orders"
headers = {
    "Authorization": f'Bearer {os.environ["MIRAKL_API_KEY"]}'
}

response = requests.get(api_url, headers=headers)
orders = response.json().get("orders", [])

# === Sheet leegmaken + kopregel zetten ===
sheet.clear()
sheet.append_row([
    "Order ID", "Orderdatum", "Klantnaam", "E-mail", "Telefoon", "Adres",
    "Postcode", "Plaats", "Land", "Product", "EAN", "SKU", "Aantal", "Prijs",
    "Verzendmethode", "Leverdatum", "Orderstatus", "Totaalbedrag"
])

# === Orders verwerken ===
for order in orders:
    customer = order["customer"]
    address = order["shipping"]["address"]
    order_state = order.get("order_state", "")
    order_date = order.get("created_date", "")
    total_price = order.get("total_price", "")
    
    for line in order["order_lines"]:
        product = line.get("product", {})
        offer = line.get("offer", {})
        sheet.append_row([
            order["id"],
            order_date,
            f'{customer.get("firstname", "")} {customer.get("lastname", "")}',
            customer.get("email", ""),
            customer.get("phone", ""),
            f'{address.get("street_1", "")} {address.get("street_2", "")}',
            address.get("zip_code", ""),
            address.get("city", ""),
            address.get("country", ""),
            line.get("product_title", ""),
            product.get("ean", ""),
            offer.get("sku", ""),
            line.get("quantity", ""),
            line.get("price", ""),
            line.get("shipping_type_code", ""),
            line.get("delivery_deadline", ""),
            order_state,
            total_price
        ])
