"""
Laptops scraper — https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops
A legitimate scraping-practice website by WebScraper.io.
"""
import time
import re
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

BASE_URL = (
    "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops?page={}"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PriceBot/1.0)"}


def fetch_laptops(max_pages: int = 2) -> list[dict]:
    products = []

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page)
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            items = soup.select("div.product-wrapper")
            if not items:
                # Fallback selector
                items = soup.select("div.thumbnail")

            for item in items:
                # Title
                title_tag = item.select_one("a.title") or item.select_one(".title")
                title = title_tag.get_text(strip=True) if title_tag else "Unknown Laptop"
                title = title_tag["title"] if title_tag and title_tag.has_attr("title") else title

                # Price
                price_tag = item.select_one("h4.price") or item.select_one(".price")
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = re.sub(r"[^\d.]", "", price_text)

                # Description / specs
                desc_tag = item.select_one("p.description") or item.select_one(".description")
                desc = desc_tag.get_text(strip=True) if desc_tag else ""

                # Rating stars
                stars = len(item.select("span.glyphicon-star:not(.glyphicon-star-empty)"))
                if not stars:
                    stars = 3  # default

                # Review count
                review_tag = item.select_one("p.ratings span") or item.select_one(".ratings")
                reviews = 0
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
                    "description": desc[:120],
                    "rating":      stars,
                    "reviews":     reviews,
                    "in_stock":    True,
                    "category":    "laptops",
                    "source_url":  "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
                })

            time.sleep(REQUEST_DELAY)

        except Exception as exc:
            print(f"[laptops_scraper] Page {page} error: {exc}")
            continue

    return products


if __name__ == "__main__":
    laptops = fetch_laptops(max_pages=1)
    print(f"Total laptops: {len(laptops)}")
    for l in laptops[:5]:
        print(l)