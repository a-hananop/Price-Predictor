"""
Paints & Art Supplies scraper.
Uses two sources:
  1. Fake Store API (https://fakestoreapi.com) — free JSON product API
  2. Scrapeme.live demo shop (https://scrapeme.live/shop/) for additional items

Products are re-labelled as art/paint supplies for demo purposes.
"""
import time
import re
import random
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PriceBot/1.0)"}

# Paint product name mapping to make FakeStore items sound like paints
PAINT_NAMES = [
    "Premium Acrylic Paint Set 24 Colors",
    "Professional Watercolor Palette",
    "Artist Grade Oil Paint Kit 12 Tubes",
    "Interior Latex Paint – Eggshell White",
    "Exterior Weather-Shield Paint 5L",
    "Chalk Paint – Vintage Blue 1L",
    "Metallic Craft Paint Bundle",
    "Eco-Friendly Primer & Undercoat",
    "Non-Toxic Kids Finger Paint Set",
    "Spray Paint – Matte Black 400ml",
    "Glass Paint – Stained Effect Kit",
    "Floor Paint – Anti-Slip Grey 2.5L",
    "Gloss Enamel Paint – Racing Red",
    "Wood Stain & Varnish Combo",
    "Magnetic Chalkboard Paint 1L",
    "Rust Converter & Metal Paint",
    "Fabric & Textile Paint 10 Colors",
    "Glow-in-Dark Paint Set",
    "Encaustic Hot Wax Art Kit",
    "Gouache Paint 36 Colors Studio Set",
]


def _fetch_from_fakestoreapi() -> list[dict]:
    """Fetch electronics/jewelry from FakeStore and re-skin as paints."""
    url = "https://fakestoreapi.com/products"
    products = []
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        for i, item in enumerate(data):
            price = float(item.get("price", 0))
            if price <= 0:
                continue

            name = PAINT_NAMES[i % len(PAINT_NAMES)]
            rating_info = item.get("rating", {})
            rating = min(5, max(1, round(float(rating_info.get("rate", 3)))))

            products.append({
                "product":     name,
                "price":       round(price * 0.4 + 5, 2),   # realistic paint pricing
                "description": item.get("description", "")[:120],
                "rating":      rating,
                "reviews":     int(rating_info.get("count", 0)),
                "in_stock":    True,
                "category":    "paints",
                "source_url":  "https://fakestoreapi.com",
            })
    except Exception as exc:
        print(f"[paints_scraper] FakeStore error: {exc}")
    return products


def _fetch_from_scrapeme(max_pages: int = 2) -> list[dict]:
    """Scrape scrapeme.live (WooCommerce test shop)."""
    products = []
    for page in range(1, max_pages + 1):
        url = f"https://scrapeme.live/shop/page/{page}/"
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select("li.product")

            for i, item in enumerate(items):
                title_tag = item.select_one("h2.woocommerce-loop-product__title")
                price_tag = item.select_one("span.price bdi") or item.select_one(".price")
                title = title_tag.get_text(strip=True) if title_tag else f"Art Paint #{i}"
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = re.sub(r"[^\d.]", "", price_text)

                try:
                    price = float(price_clean)
                except ValueError:
                    continue

                # Re-label as paint product
                paint_name = PAINT_NAMES[(i + page * 8) % len(PAINT_NAMES)]

                products.append({
                    "product":     f"{paint_name} ({title})",
                    "price":       round(price * 0.3 + 8, 2),
                    "description": f"High-quality {paint_name.lower()} for professionals and hobbyists.",
                    "rating":      random.randint(3, 5),
                    "reviews":     random.randint(5, 200),
                    "in_stock":    True,
                    "category":    "paints",
                    "source_url":  "https://scrapeme.live/shop",
                })

            time.sleep(REQUEST_DELAY)
        except Exception as exc:
            print(f"[paints_scraper] Scrapeme page {page} error: {exc}")
            continue

    return products


def fetch_paints(max_pages: int = 2) -> list[dict]:
    products = _fetch_from_fakestoreapi()
    products += _fetch_from_scrapeme(max_pages)
    # Deduplicate on product name
    seen = set()
    unique = []
    for p in products:
        if p["product"] not in seen:
            seen.add(p["product"])
            unique.append(p)
    return unique


if __name__ == "__main__":
    paints = fetch_paints(max_pages=1)
    print(f"Total paints: {len(paints)}")
    for p in paints[:5]:
        print(p)