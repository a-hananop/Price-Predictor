"""
verify_scrapers.py
──────────────────
Tests each scraper to ensure it returns valid product lists for the Pakistan market.
"""
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers import fetch_category

def test_scraper(category):
    print(f"--- Testing {category} ---")
    try:
        products = fetch_category(category, max_pages=1)
        print(f"Success! Found {len(products)} products.")
        if products:
            print(f"Sample: {products[0]['product']} - Rs. {products[0]['price']}")
            # Basic validation
            assert 'product' in products[0]
            assert 'price' in products[0]
            assert isinstance(products[0]['price'], (int, float))
            assert products[0]['category'] == category
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    categories = ["mobiles", "laptops", "electronics", "books", "paints"]
    results = {}
    for cat in categories:
        results[cat] = test_scraper(cat)
    
    print("\n--- Summary ---")
    all_ok = True
    for cat, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"{cat:12}: {status}")
        if not ok: all_ok = False
    
    if all_ok:
        print("\nAll scrapers verified successfully!")
        sys.exit(0)
    else:
        print("\nSome scrapers failed verification.")
        sys.exit(1)
