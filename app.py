"""
app.py — Pakistan Electronics Intelligence — API Server
────────────────────────────────────────────────────────
Electronics-only. 30+ Pakistani stores. Distance/fuel/route optimization.
"""
from __future__ import annotations
import threading
from flask import Flask, jsonify, request, render_template
from config import BRANCHES, CATEGORY_META, GOOGLE_MAPS_API_KEY, STORES, PHYSICAL_STORES, ONLINE_STORES
from scrapers import fetch_category, SCRAPER_MAP
from services.prediction_service import rank_branches
from services.decision_service import recommend, multi_category_plan

app = Flask(__name__)

@app.after_request
def cors_headers(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# ─── In-memory product cache  ─────────────────────────────────────────────────
_cache: dict[str, list[dict]] = {}
_cache_lock = threading.Lock()


def _get_products(category: str = "electronics", max_pages: int = 2, query: str = None) -> list[dict]:
    cache_key = f"electronics_{query}" if query else "electronics"
    with _cache_lock:
        if cache_key not in _cache:
            _cache[cache_key] = fetch_category("electronics", max_pages, query=query)
        return _cache[cache_key]


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", google_maps_key=GOOGLE_MAPS_API_KEY)


@app.route("/api/categories")
def api_categories():
    return jsonify({
        "categories": [
            {"id": k, **v} for k, v in CATEGORY_META.items()
        ]
    })


@app.route("/api/branches")
def api_branches():
    return jsonify({"branches": BRANCHES})


@app.route("/api/stores")
def api_stores():
    """List all 30+ stores with type info."""
    return jsonify({
        "total": len(STORES),
        "physical_count": len(PHYSICAL_STORES),
        "online_count": len(ONLINE_STORES),
        "stores": STORES,
    })


@app.route("/api/products/electronics")
@app.route("/api/products/<category>")
def api_products(category: str = "electronics"):
    pages = int(request.args.get("pages", 2))
    try:
        products = _get_products("electronics", pages)
        return jsonify({
            "category": "electronics",
            "count":    len(products),
            "products": products,   # Return ALL products, no cap
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/scrape/electronics", methods=["POST"])
@app.route("/api/scrape/<category>", methods=["POST"])
def api_scrape(category: str = "electronics"):
    """Force-refresh the cache."""
    pages = int(request.json.get("pages", 2)) if request.json else 2
    try:
        with _cache_lock:
            _cache["electronics"] = fetch_category("electronics", pages)
        return jsonify({"status": "ok", "count": len(_cache["electronics"])})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/search", methods=["GET"])
def search_products():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        results = _get_products("electronics", max_pages=1, query=query)

        return jsonify({
            "query": query,
            "count": len(results),
            "products": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    """
    Find the best branch + product for a user's location.

    Body JSON:
      user_lat   float  (required)
      user_lon   float  (required)
      category   str    (optional, defaults to 'electronics')
      budget     float  (optional)
      priority   str    "total_cost" | "price" | "distance"  (optional)
      pages      int    (optional, default 2)
    """
    data = request.json or {}
    user_lat  = data.get("user_lat")
    user_lon  = data.get("user_lon")
    budget    = data.get("budget")
    priority  = data.get("priority", "total_cost")
    pages     = int(data.get("pages", 2))

    if user_lat is None or user_lon is None:
        return jsonify({"error": "user_lat and user_lon are required"}), 400

    try:
        products = _get_products("electronics", pages)
        ranked   = rank_branches(
            float(user_lat), float(user_lon),
            "electronics", products,
            budget=float(budget) if budget else None,
            priority=priority,
        )
        decision = recommend(ranked)
        return jsonify(decision)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


@app.route("/api/multi-optimize", methods=["POST"])
def api_multi_optimize():
    """
    Multi-store optimization (kept for backward compatibility).
    Since we're electronics-only, this optimizes across stores.
    """
    data       = request.json or {}
    user_lat   = data.get("user_lat")
    user_lon   = data.get("user_lon")
    priority   = data.get("priority", "total_cost")

    if user_lat is None or user_lon is None:
        return jsonify({"error": "user_lat and user_lon are required"}), 400

    try:
        products = _get_products("electronics", 2)
        ranked   = rank_branches(
            float(user_lat), float(user_lon),
            "electronics", products, priority=priority,
        )
        decision = recommend(ranked)
        return jsonify(decision)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)