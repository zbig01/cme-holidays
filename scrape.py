import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.cmegroup.com/tools-information/holiday-calendar.html"

r = requests.get(URL, timeout=20)
soup = BeautifulSoup(r.text, "lxml")

rows = soup.select("table tbody tr")

data = []

for row in rows:
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) < 2:
        continue

    date = cols[0]
    name = cols[1]

    entry = {
        "date": date,
        "name": name,
        "early_close": None,
        "sunday_open": None
    }

    data.append(entry)

with open("crosstrade.json", "w") as f:
    json.dump(data, f, indent=2)
