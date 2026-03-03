"""
HomeShopping Scraper — https://homeshopping.pk/
Real-time scraper for various categories in Pakistan.
"""
import time
import re
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

BASE_URL = "https://homeshopping.pk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_homeshopping(category: str = "mobiles", max_pages: int = 1, query: str = None) -> list[dict]:
    products = []
    
    if query:
        url_template = f"https://homeshopping.pk/search.php?search_query={query}&page={{}}"
    else:
        # Categories mapping for HomeShopping
        hs_categories = {
            "mobiles": "categories/Mobile-Phones-Price-Pakistan",
            "laptops": "categories/Laptops-Price-Pakistan",
            "electronics": "categories/Smart-Watches-Price-Pakistan",
            "books": "categories/Books-Price-Pakistan",
        }
        slug = hs_categories.get(category, "categories/Mobile-Phones-Price-Pakistan")
        url_template = f"https://homeshopping.pk/{slug}/?page={{}}"
    
    for page in range(1, max_pages + 1):
        url = url_template.format(page)
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # HomeShopping product cards
            items = soup.select(".product-box") or soup.select(".Inner-product-box") or soup.select(".product")
            
            for item in items:
                # Title
                title_tag = item.select_one(".product-title") or item.select_one("h3") or item.select_one("a")
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
                    "description": f"Available on HomeShopping.pk",
                    "rating":      4.0,
                    "reviews":     5,
                    "in_stock":    True,
                    "category":    category if not query else "search",
                    "source_url":  url,
                })

            time.sleep(REQUEST_DELAY)

        except Exception as exc:
            print(f"[homeshopping_scraper] Page {page} error: {exc}")
            continue

    return products

if __name__ == "__main__":
    items = fetch_homeshopping(max_pages=1)
    print(f"Total items: {len(items)}")
    for p in items[:5]:
        print(p)
