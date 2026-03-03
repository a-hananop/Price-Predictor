"""
prediction_service.py
─────────────────────
Scores every (branch × product) combination for a given user location.
Returns a ranked list with estimated grand total cost.
"""
from __future__ import annotations
import random
from config import BRANCHES, CATEGORY_META
from utils.distance import full_trip_analysis


def _assign_price_variation(base_price: float, branch_id: str) -> float:
    """
    Different branches may have slightly different prices (±10%).
    Uses the branch_id as a deterministic seed so results are stable.
    """
    rng = random.Random(hash(branch_id))
    factor = rng.uniform(0.92, 1.08)
    return round(base_price * factor, 2)


def rank_branches(
    user_lat: float,
    user_lon: float,
    category: str,
    products: list[dict],
    budget: float | None = None,
    priority: str = "total_cost",   # "total_cost" | "price" | "distance"
) -> list[dict]:
    """
    For each branch that carries `category`, calculate travel cost +
    the cheapest available product price at that branch.

    Returns a list of branch+product dicts, sorted by the chosen priority.
    """
    if not products:
        return []

    # Filter branches that carry the requested category
    eligible = [b for b in BRANCHES if category in b.get("categories", [])]

    results = []
    for branch in eligible:
        # Find the best (cheapest) product in this category
        # Simulate that each branch may have a slightly different price
        best_product = None
        best_price = float("inf")

        for prod in products:
            if prod.get("category") != category:
                continue
            branch_price = _assign_price_variation(prod["price"], branch["id"])
            if branch_price < best_price:
                best_price   = branch_price
                best_product = {**prod, "price": branch_price}

        if best_product is None:
            continue

        if budget and best_price > budget:
            continue

        # Travel analysis
        trip = full_trip_analysis(
            user_lat, user_lon,
            branch["lat"], branch["lon"],
            product_price=best_price,
        )

        results.append({
            "branch":         branch,
            "best_product":   best_product,
            "distance_km":    trip["distance_km"],
            "duration_min":   trip["duration_min"],
            "fuel_cost":      trip["fuel_cost"],
            "time_cost":      trip["time_cost"],
            "travel_cost":    trip["total_cost"],
            "product_price":  best_price,
            "grand_total":    trip["grand_total"],
            "via":            trip["via"],
            "category_meta":  CATEGORY_META.get(category, {}),
            "score":          _score(trip, priority),
        })

    key = {
        "total_cost": "grand_total",
        "price":      "product_price",
        "distance":   "distance_km",
    }.get(priority, "grand_total")

    results.sort(key=lambda x: x[key])
    return results


def _score(trip: dict, priority: str) -> float:
    """Composite score — lower is better."""
    if priority == "price":
        return trip["product_price"]
    if priority == "distance":
        return trip["distance_km"]
    # Weighted: 50% price, 30% fuel, 20% time
    return trip["product_price"] * 0.5 + trip["fuel_cost"] * 0.3 + trip["time_cost"] * 0.2