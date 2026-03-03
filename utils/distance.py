"""
distance.py — distance and travel-cost calculations.

Primary:  Google Maps Distance Matrix API (real road distances + duration)
Fallback: Haversine formula (straight-line "as the crow flies")
"""
from __future__ import annotations
import math
import requests
from config import GOOGLE_MAPS_API_KEY, FUEL_COST_PER_KM, TIME_VALUE_PER_HOUR, AVG_SPEED_KMH

GMAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


# ─── Haversine fallback ────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in kilometres between two points."""
    R = 6_371.0  # Earth radius km
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lon2 - lon1)
    a = math.sin(dφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ─── Google Maps Distance Matrix ──────────────────────────────────────────────

def _gmaps_distance(
    origin_lat: float, origin_lon: float,
    dest_lat: float,   dest_lon: float,
) -> dict | None:
    """Call the Distance Matrix API. Returns dict or None on error/no key."""
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY.startswith("YOUR_"):
        return None

    params = {
        "origins":      f"{origin_lat},{origin_lon}",
        "destinations": f"{dest_lat},{dest_lon}",
        "units":        "metric",
        "key":          GOOGLE_MAPS_API_KEY,
    }
    try:
        r = requests.get(GMAPS_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return None
        return {
            "distance_km":  element["distance"]["value"] / 1000,
            "duration_min": element["duration"]["value"] / 60,
            "via":          "google_maps",
        }
    except Exception as exc:
        print(f"[distance] Google Maps error: {exc}")
        return None


# ─── Public API ───────────────────────────────────────────────────────────────

def get_distance(
    origin_lat: float, origin_lon: float,
    dest_lat: float,   dest_lon: float,
) -> dict:
    """
    Return distance info dict:
      distance_km, duration_min, via
    Tries Google Maps first; falls back to Haversine + estimated time.
    """
    result = _gmaps_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    if result:
        return result

    km = haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)
    # Road distance is ~1.3× crow-flies for typical routes
    road_km = km * 1.3
    duration = (road_km / AVG_SPEED_KMH) * 60   # minutes
    return {
        "distance_km":  round(road_km, 2),
        "duration_min": round(duration, 1),
        "via":          "haversine_estimate",
    }


def travel_cost(distance_km: float, duration_min: float) -> dict:
    """
    Estimate total travel cost (one-way).
    Returns:
      fuel_cost    — fuel price for the trip
      time_cost    — opportunity cost of travel time
      total_cost   — combined travel overhead
    """
    fuel  = round(distance_km * FUEL_COST_PER_KM, 2)
    time_ = round((duration_min / 60) * TIME_VALUE_PER_HOUR, 2)
    return {
        "fuel_cost":  fuel,
        "time_cost":  time_,
        "total_cost": round(fuel + time_, 2),
    }


def full_trip_analysis(
    origin_lat: float, origin_lon: float,
    dest_lat: float,   dest_lon: float,
    product_price: float = 0.0,
) -> dict:
    """
    One-stop function: distance + travel cost + product price = total spend.
    """
    dist = get_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    cost = travel_cost(dist["distance_km"], dist["duration_min"])
    total = round(product_price + cost["total_cost"], 2)
    return {
        **dist,
        **cost,
        "product_price": product_price,
        "grand_total":   total,
    }