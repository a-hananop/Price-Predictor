"""
Telemart Scraper — https://www.telemart.pk/
Real-time scraper for mobile phones and electronics in Pakistan.
"""
import time
import re
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

BASE_URL = "https://www.telemart.pk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_telemart(category: str = "mobiles", max_pages: int = 1, query: str = None) -> list[dict]:
    products = []
    
    if query:
        url_template = f"https://www.telemart.pk/search?query={query}&page={{}}"
    else:
        # Categories mapping for Telemart
        tm_categories = {
            "mobiles": "mobile-phones",
            "laptops": "laptops",
            "electronics": "smart-watches",
        }
        slug = tm_categories.get(category, "mobile-phones")
        url_template = f"https://www.telemart.pk/{slug}?page={{}}"
    
    for page in range(1, max_pages + 1):
        url = url_template.format(page)
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Telemart product cards
            items = soup.select(".product-box") or soup.select(".product-card") or soup.select(".card-product")
            if not items:
                items = soup.find_all("div", class_=re.compile(r"product.*card|card.*product|grid-item"))

            for item in items:
                # Title
                title_tag = item.select_one(".product-title") or item.select_one("h3") or item.select_one(".name") or item.select_one(".title")
                title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

                # Price
                price_tag = item.select_one(".product-price") or item.select_one(".price") or item.select_one(".actual-price") or item.select_one(".current-price")
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = re.sub(r"[^\d]", "", price_text)

                # Rating
                rating = 4.0 # default
                rating_tag = item.select_one(".rating") or item.select_one(".stars")
                if rating_tag:
                    try:
                        style = rating_tag.get("style", "")
                        if "width" in style:
                            m = re.search(r"(\d+)%", style)
                            if m:
                                rating = float(m.group(1)) / 20.0
                    except:
                        pass

                try:
                    price = float(price_clean)
                except ValueError:
                    continue

                if price <= 0:
                    continue

                products.append({
                    "product":     title,
                    "price":       price,
                    "description": f"Available on Telemart.pk",
                    "rating":      rating,
                    "reviews":     12, 
                    "in_stock":    True,
                    "category":    category if not query else "search",
                    "source_url":  url,
                })

            time.sleep(REQUEST_DELAY)

        except Exception as exc:
            print(f"[telemart_scraper] Page {page} error: {exc}")
            continue

    return products


if __name__ == "__main__":
    items = fetch_telemart(max_pages=1)
    print(f"Total items: {len(items)}")
    for p in items[:5]:
        print(p)
