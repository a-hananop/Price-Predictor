"""
prediction_service.py
─────────────────────
Scores every (branch × product) combination for a given user location.
Returns a ranked list with estimated grand total cost.

Products are matched to their SOURCE STORE so each store only shows
products it actually carries.
"""
from __future__ import annotations
from config import BRANCHES, CATEGORY_META, STORES
from utils.distance import full_trip_analysis


def _match_store_to_branch(source_store: str) -> dict | None:
    """Find the branch that matches a product's source_store name."""
    source_lower = source_store.strip().lower()
    for branch in BRANCHES:
        if branch["name"].strip().lower() == source_lower:
            return branch
    # Fuzzy: check if store name contains branch name or vice versa
    for branch in BRANCHES:
        bname = branch["name"].strip().lower()
        if bname in source_lower or source_lower in bname:
            return branch
    return None


def _keyword_match(product_name: str, query: str) -> bool:
    """Check if a product name matches the search query (keyword-based)."""
    if not query:
        return True
    query_lower = query.strip().lower()
    product_lower = product_name.strip().lower()
    # All query words must appear in the product name
    query_words = query_lower.split()
    return all(word in product_lower for word in query_words)


def rank_branches(
    user_lat: float,
    user_lon: float,
    category: str,
    products: list[dict],
    budget: float | None = None,
    priority: str = "total_cost",   # "total_cost" | "price" | "distance"
    query: str | None = None,
) -> list[dict]:
    """
    For each branch, find products FROM THAT SPECIFIC STORE,
    calculate travel cost, and rank by the chosen priority.

    Each branch shows its OWN best product (matched by source_store).
    If query is provided, products are also filtered by keyword relevance.
    """
    if not products:
        return []

    # ── Step 1: Group products by their source store (branch) ──────────
    branch_products: dict[str, list[dict]] = {}  # branch_id -> [products]
    unmatched_products: list[dict] = []

    for prod in products:
        if prod.get("category") != category:
            continue

        # Filter by search query relevance
        if query and not _keyword_match(prod.get("product", ""), query):
            continue

        source_store = prod.get("source_store", "")
        branch = _match_store_to_branch(source_store)

        if branch:
            bid = branch["id"]
            if bid not in branch_products:
                branch_products[bid] = []
            branch_products[bid].append(prod)
        else:
            unmatched_products.append(prod)

    # ── Step 2: For each branch with products, calculate travel + costs ──
    results = []
    branch_by_id = {b["id"]: b for b in BRANCHES}

    for bid, prods in branch_products.items():
        branch = branch_by_id.get(bid)
        if not branch:
            continue

        # Only physical stores have meaningful distance calculations
        is_physical = branch.get("type", "physical") == "physical"

        # Find the best (cheapest) product at this specific store
        prods_sorted = sorted(prods, key=lambda p: p.get("price", float("inf")))

        for prod in prods_sorted:
            price = prod.get("price", 0)
            if price <= 0:
                continue

            # Budget filter: skip if item price alone exceeds budget
            if budget and price > budget:
                continue

            # Travel analysis
            if is_physical:
                trip = full_trip_analysis(
                    user_lat, user_lon,
                    branch["lat"], branch["lon"],
                    product_price=price,
                )
            else:
                # Online stores: no travel cost
                trip = {
                    "distance_km": 0,
                    "duration_min": 0,
                    "fuel_cost": 0,
                    "time_cost": 0,
                    "total_cost": 0,
                    "product_price": price,
                    "grand_total": price,
                    "via": "online",
                }

            grand_total = trip["grand_total"]

            # Budget filter on grand total (item + travel)
            if budget and grand_total > budget:
                continue

            result = {
                "branch":         branch,
                "best_product":   prod,
                "distance_km":    trip["distance_km"],
                "duration_min":   trip["duration_min"],
                "fuel_cost":      trip["fuel_cost"],
                "time_cost":      trip["time_cost"],
                "travel_cost":    trip["total_cost"],
                "product_price":  price,
                "grand_total":    grand_total,
                "via":            trip["via"],
                "category_meta":  CATEGORY_META.get(category, {}),
                "score":          _score(trip, priority),
            }
            results.append(result)
            break  # Only keep the best (cheapest) product per store

    # ── Step 3: Sort by priority ──────────────────────────────────────
    sort_key = {
        "total_cost": "grand_total",
        "price":      "product_price",
        "distance":   "distance_km",
    }.get(priority, "grand_total")

    results.sort(key=lambda x: x[sort_key])
    return results


def _score(trip: dict, priority: str) -> float:
    """Composite score — lower is better."""
    if priority == "price":
        return trip.get("product_price", 0)
    if priority == "distance":
        return trip.get("distance_km", 0)
    # Weighted: 50% price, 30% fuel, 20% time
    return (
        trip.get("product_price", 0) * 0.5
        + trip.get("fuel_cost", 0) * 0.3
        + trip.get("time_cost", 0) * 0.2
    )