"""
Electronics scraper — https://fakestoreapi.com/products/category/electronics
Free public API — no scraping restrictions.
"""
import requests
from config import REQUEST_TIMEOUT

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PriceBot/1.0)"}
API_URL = "https://fakestoreapi.com/products/category/electronics"


def fetch_electronics() -> list[dict]:
    products = []
    try:
        r = requests.get(API_URL, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        for item in data:
            price = float(item.get("price", 0))
            if price <= 0:
                continue

            rating_info = item.get("rating", {})
            rating = min(5, max(1, round(float(rating_info.get("rate", 3)))))

            products.append({
                "product":     item.get("title", "Electronics Item"),
                "price":       round(price, 2),
                "description": item.get("description", "")[:120],
                "rating":      rating,
                "reviews":     int(rating_info.get("count", 0)),
                "in_stock":    True,
                "category":    "electronics",
                "source_url":  "https://fakestoreapi.com",
            })

    except Exception as exc:
        print(f"[electronics_scraper] Error: {exc}")

    return products


if __name__ == "__main__":
    items = fetch_electronics()
    print(f"Total electronics: {len(items)}")
    for i in items[:5]:
        print(i)