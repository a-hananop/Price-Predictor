"""
CZone Scraper — https://www.czone.com.pk/
Real-time scraper for laptops and electronics in Pakistan.
"""
import time
import re
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

BASE_URL = "https://www.czone.com.pk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_czone(category: str = "laptops", max_pages: int = 1, query: str = None) -> list[dict]:
    products = []
    
    if query:
        url_template = f"https://www.czone.com.pk/search.aspx?kw={query}&page={{}}"
    else:
        # Categories mapping for CZone
        cz_categories = {
            "laptops": "laptops-pakistan-ppt.74.aspx",
            "electronics": "graphic-cards-pakistan-ppt.14.aspx", # default to high demand
        }
        slug = cz_categories.get(category, "laptops-pakistan-ppt.74.aspx")
        url_template = f"https://www.czone.com.pk/{slug}?page={{}}"
    
    for page in range(1, max_pages + 1):
        url = url_template.format(page)
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # CZone product cards
            items = soup.select(".product") or soup.select(".product-box")
            
            for item in items:
                # Title
                title_tag = item.select_one(".title") or item.select_one("h4") or item.select_one("a")
                title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

                # Price
                price_tag = item.select_one(".price") or item.select_one(".actual-price")
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = re.sub(r"[^\d]", "", price_text)

                try:
                    price = float(price_clean)
                except ValueError:
                    continue

                if price <= 0:
                    continue

                products.append({
                    "product":     title,
                    "price":       price,
                    "description": f"Available on CZone.pk",
                    "rating":      4.5,
                    "reviews":     20,
                    "in_stock":    True,
                    "category":    category if not query else "search",
                    "source_url":  url,
                })

            time.sleep(REQUEST_DELAY)

        except Exception as exc:
            print(f"[czone_scraper] Page {page} error: {exc}")
            continue

    return products

if __name__ == "__main__":
    items = fetch_czone(max_pages=1)
    print(f"Total items: {len(items)}")
    for p in items[:5]:
        print(p)
