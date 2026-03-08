"""
decision_service.py
────────────────────
Converts the ranked branch list into actionable decisions:
  • Best overall pick
  • Best if you want lowest price (don't care about distance)
  • Best if you want shortest trip
  • Multi-stop route if user wants several categories
"""
from __future__ import annotations


def recommend(ranked: list[dict]) -> dict:
    """
    Given a ranked list from prediction_service.rank_branches,
    return a structured recommendation object.
    """
    if not ranked:
        return {"error": "No branches found for this category and location."}

    best_overall   = ranked[0]
    cheapest_item  = min(ranked, key=lambda x: x["product_price"])

    # Only consider physical stores for "nearest" calculations
    physical_ranked = [r for r in ranked if r.get("branch", {}).get("type") == "physical"]
    nearest_branch = min(physical_ranked, key=lambda x: x["distance_km"]) if physical_ranked else best_overall

    savings_vs_nearest = round(
        nearest_branch["grand_total"] - best_overall["grand_total"], 2
    )

    advice_lines = []

    if best_overall["branch"]["id"] == cheapest_item["branch"]["id"]:
        advice_lines.append(
            f"✅ {best_overall['branch']['name']} has the best deal overall — "
            f"Rs. {best_overall['grand_total']:.0f} total (item + travel)."
        )
    else:
        advice_lines.append(
            f"💡 The cheapest item is at {cheapest_item['branch']['name']} "
            f"(Rs. {cheapest_item['product_price']:.0f}), but total cost with travel is "
            f"Rs. {cheapest_item['grand_total']:.0f}."
        )
        if savings_vs_nearest > 0:
            advice_lines.append(
                f"🏆 Choosing {best_overall['branch']['name']} saves you "
                f"Rs. {savings_vs_nearest:.0f} overall vs the nearest store."
            )

    if physical_ranked and nearest_branch["branch"]["id"] != best_overall["branch"]["id"]:
        advice_lines.append(
            f"📍 Nearest physical store: {nearest_branch['branch']['name']} "
            f"({nearest_branch['distance_km']:.1f} km, "
            f"~{nearest_branch['duration_min']:.0f} min drive)."
        )

    return {
        "best_overall":    _fmt(best_overall),
        "cheapest_item":   _fmt(cheapest_item),
        "nearest_branch":  _fmt(nearest_branch),
        "all_options":     [_fmt(r) for r in ranked],
        "advice":          advice_lines,
        "total_options":   len(ranked),
    }


def multi_category_plan(
    category_results: dict[str, list[dict]],
    user_lat: float,
    user_lon: float,
) -> dict:
    """
    Given results for multiple categories, suggest a combined route
    that minimises total distance and cost.

    Returns an ordered list of stops plus combined cost summary.
    """
    from utils.distance import haversine_km

    stops = []
    total_product_cost = 0.0
    total_travel_cost  = 0.0

    for category, ranked in category_results.items():
        if not ranked:
            continue
        best = ranked[0]
        stops.append({
            "category":       category,
            "branch":         best["branch"],
            "product":        best["best_product"]["product"],
            "product_price":  best["product_price"],
            "distance_from_user_km": best["distance_km"],
        })
        total_product_cost += best["product_price"]
        total_travel_cost  += best["travel_cost"]

    # Greedy nearest-neighbour ordering of stops (starting from user)
    ordered = []
    remaining = stops[:]
    current_lat, current_lon = user_lat, user_lon
    while remaining:
        nearest = min(
            remaining,
            key=lambda s: haversine_km(current_lat, current_lon,
                                       s["branch"]["lat"], s["branch"]["lon"])
        )
        ordered.append(nearest)
        current_lat = nearest["branch"]["lat"]
        current_lon = nearest["branch"]["lon"]
        remaining.remove(nearest)

    return {
        "ordered_stops":       ordered,
        "total_product_cost":  round(total_product_cost, 2),
        "total_travel_cost":   round(total_travel_cost, 2),
        "estimated_grand_total": round(total_product_cost + total_travel_cost, 2),
    }


def _fmt(r: dict) -> dict:
    """Return a clean, serialisable dict for the API response."""
    return {
        "branch_id":      r["branch"]["id"],
        "branch_name":    r["branch"]["name"],
        "branch_type":    r["branch"].get("type", "physical"),
        "branch_url":     r["branch"].get("url", ""),
        "city":           r["branch"]["city"],
        "address":        r["branch"]["address"],
        "lat":            r["branch"]["lat"],
        "lon":            r["branch"]["lon"],
        "phone":          r["branch"].get("phone", ""),
        "rating":         r["branch"].get("rating", 0),
        "product":        r["best_product"]["product"],
        "product_price":  r["product_price"],
        "product_rating": r["best_product"].get("rating", 0),
        "distance_km":    r["distance_km"],
        "duration_min":   r["duration_min"],
        "fuel_cost":      r["fuel_cost"],
        "time_cost":      r["time_cost"],
        "travel_cost":    r["travel_cost"],
        "grand_total":    r["grand_total"],
        "via":            r.get("via", "estimate"),
        "score":          r.get("score", 0),
    }