"""
PriceOye Scraper — https://priceoye.pk/
Real-time scraper for mobile phones and electronics in Pakistan.
"""
import time
import re
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

BASE_URL = "https://priceoye.pk/mobiles"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_priceoye(category: str = "mobiles", max_pages: int = 1, query: str = None) -> list[dict]:
    products = []
    
    if query:
        # If searching, use the search URL
        url_template = f"https://priceoye.pk/search?q={query}&page={{}}"
    else:
        # Categories mapping for PriceOye
        po_categories = {
            "mobiles": "mobiles",
            "laptops": "laptops",
            "electronics": "smart-watches",
        }
        slug = po_categories.get(category, "mobiles")
        url_template = f"https://priceoye.pk/{slug}?page={{}}"
    
    for page in range(1, max_pages + 1):
        url = url_template.format(page)
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # PriceOye product cards
            items = soup.select(".product-list .productBox") or soup.select(".p-list .p-box") or soup.select(".productBox")

            for item in items:
                # Title
                title_tag = item.select_one(".p-title") or item.select_one(".detail-box .name") or item.select_one("h4")
                title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

                # Price
                price_tag = item.select_one(".price-box .price") or item.select_one(".p-price") or item.select_one(".price")
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = re.sub(r"[^\d]", "", price_text)

                # Rating
                rating_tag = item.select_one(".p-rating") or item.select_one(".rating")
                rating_text = rating_tag.get_text(strip=True) if rating_tag else "4.5"
                try:
                    m = re.search(r"[\d.]+", rating_text)
                    rating = float(m.group()) if m else 4.5
                except:
                    rating = 4.5

                # Reviews
                reviews = 0
                review_tag = item.select_one(".p-reviews") or item.select_one(".reviews")
                if review_tag:
                    m = re.search(r"\d+", review_tag.get_text())
                    reviews = int(m.group()) if m else 0

                try:
                    price = float(price_clean)
                except ValueError:
                    continue

                if price <= 0:
                    continue

                products.append({
                    "product":     title,
                    "price":       price,
                    "description": f"Available on PriceOye.pk",
                    "rating":      rating,
                    "reviews":     reviews,
                    "in_stock":    True,
                    "category":    category if not query else "search",
                    "source_url":  url,
                })

            time.sleep(REQUEST_DELAY)

        except Exception as exc:
            print(f"[priceoye_scraper] Page {page} error: {exc}")
            continue

    return products


if __name__ == "__main__":
    items = fetch_priceoye(max_pages=1)
    print(f"Total items: {len(items)}")
    for p in items[:5]:
        print(p)
