"""
scrapers/__init__.py — Electronics-only scraper dispatcher
──────────────────────────────────────────────────────────
Single entry point: fetch_category('electronics') or fetch_all()
"""
from scrapers.universal_scraper import fetch_all_stores

# Keep SCRAPER_MAP for backward compatibility with app.py
SCRAPER_MAP = {
    "electronics": [fetch_all_stores],
}


def fetch_category(category: str = "electronics", max_pages: int = 2, query: str = None) -> list[dict]:
    """
    Fetch products for the given category.
    Since we're electronics-only, always delegates to universal_scraper.
    """
    return fetch_all_stores(query=query, max_per_store=20)
