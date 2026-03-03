import json, time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_cme():
    url = "https://www.cmegroup.com/tools-information/holiday-calendar.html"
    
    with sync_playwright() as p:
        # 1. Stealth Launch: Turn off headless indicators
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2. Hard Wait: Give the JS-heavy table 10 seconds to render
            print("Waiting for table to render...")
            time.sleep(10) 
            
            # Grab content
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            
            # 3. Flexible Selecting: Find any table that looks like the holiday one
            rows = soup.find_all("tr")
            
            data = []
            for r in rows:
                cols = [c.get_text(strip=True) for c in r.find_all("td")]
                # Filter for rows that actually have data (Date, Holiday Name, etc.)
                if len(cols) >= 2 and any(char.isdigit() for char in cols[0]):
                    data.append({
                        "date": cols[0],
                        "name": cols[1],
                        "details": cols[2] if len(cols) > 2 else ""
                    })
            
            if not data:
                print("Warning: No rows found. CME might be blocking the request.")
            else:
                with open("crosstrade.json", "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Success! {len(data)} holidays saved.")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_cme()