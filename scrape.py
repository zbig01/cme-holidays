import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_cme():
    url = "https://www.cmegroup.com/tools-information/holiday-calendar.html"
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        
        # Mimic a real desktop browser context
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        try:
            # networkidle waits for the JavaScript tables to finish loading
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            
            # Select the rows from the holiday table
            rows = soup.select("table tbody tr")
            
            data = []
            for r in rows:
                cols = [c.get_text(strip=True) for c in r.find_all("td")]
                if len(cols) >= 2:
                    # Mapping data to your trading dashboard format
                    data.append({
                        "date": cols[0],
                        "name": cols[1],
                        "early_close": cols[2] if len(cols) > 2 else None,
                        "sunday_open": cols[3] if len(cols) > 3 else None
                    })
            
            # Save the result
            with open("crosstrade.json", "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"Success! {len(data)} holidays saved to crosstrade.json")
            
        except Exception as e:
            print(f"Error during scrape: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_cme()