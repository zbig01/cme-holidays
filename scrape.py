import requests
import json
import sys
import re

def get_free_proxies():
    print("Fetching fresh free proxies...")
    url = "https://www.sslproxies.org/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Regex to find IP:Port patterns in the table
        proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', response.text)
        print(f"Found {len(proxies)} potential proxies.")
        return proxies
    except Exception as e:
        print(f"Could not fetch proxy list: {e}")
        return []

def get_actual_data():
    # The actual 'Side Door' endpoint for 2026 holiday data
    target_url = "https://www.cmegroup.com/CmeWS/mvc/ProductSlate/V2/List?id=2026-holidays&category=holiday-calendar"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.cmegroup.com/tools-information/holiday-calendar.html"
    }

    proxy_list = get_free_proxies()
    
    # We try up to 10 proxies to find one that works
    for proxy_ip in proxy_list[:10]:
        proxies = {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"}
        print(f"Trying proxy: {proxy_ip}...")
        
        try:
            response = requests.get(target_url, headers=headers, proxies=proxies, timeout=10)
            
            if response.status_code == 200:
                raw_data = response.json()
                final_holidays = []
                
                # Extracting the actual products/holidays from the CME JSON structure
                for group in raw_data.get('groups', []):
                    for item in group.get('products', []):
                        final_holidays.append({
                            "date": item.get('date'),
                            "holiday": item.get('name'),
                            "early_close": item.get('earlyCloseTime'),
                            "sunday_open": item.get('sundayOpenTime')
                        })
                
                if final_holidays:
                    with open("crosstrade.json", "w") as f:
                        json.dump(final_holidays, f, indent=2)
                    print(f"SUCCESS! Using {proxy_ip}, saved {len(final_holidays)} actual records.")
                    return # Exit the function on success
                    
            print(f"Proxy {proxy_ip} returned status {response.status_code}. Moving to next...")
        except Exception as e:
            print(f"Proxy {proxy_ip} failed (Timeout/Error).")

    print("Error: All proxies failed or CME block remains in place.")
    sys.exit(1)

if __name__ == "__main__":
    get_actual_data()