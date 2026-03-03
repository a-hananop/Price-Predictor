"""
Books scraper — https://books.toscrape.com
A legitimate scraping-practice website.
"""
import time
import re
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, REQUEST_DELAY

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

STAR_MAP = {
    "One":   1,
    "Two":   2,
    "Three": 3,
    "Four":  4,
    "Five":  5,
}


def fetch_books(max_pages: int = 2) -> list[dict]:
    products = []

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page)
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.find_all("article", class_="product_pod")

            for item in items:
                title = item.h3.a["title"]
                price_text = item.find("p", class_="price_color").text
                price_clean = re.sub(r"[^\d.]", "", price_text)

                # Star rating
                rating_tag = item.find("p", class_="star-rating")
                rating_word = rating_tag["class"][1] if rating_tag else "One"
                rating = STAR_MAP.get(rating_word, 1)

                # Availability
                avail_tag = item.find("p", class_="instock")
                in_stock = bool(avail_tag)

                try:
                    price = float(price_clean)
                except ValueError:
                    continue

                products.append({
                    "product":    title,
                    "price":      price,
                    "rating":     rating,
                    "in_stock":   in_stock,
                    "category":   "books",
                    "source_url": "http://books.toscrape.com",
                })

            time.sleep(REQUEST_DELAY)

        except Exception as exc:
            print(f"[books_scraper] Page {page} error: {exc}")
            continue

    return products


if __name__ == "__main__":
    books = fetch_books(max_pages=2)
    print(f"Total books: {len(books)}")
    for b in books[:5]:
        print(b)