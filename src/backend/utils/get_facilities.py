import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

from backend.utils.logging import setup_logger

logger = setup_logger(__name__)


def find_nearby_facilities(
    lat: float,
    lon: float,
    radius: int = 5000,
    facility_type: str = "pharmacy",
) -> List[Dict[str, Any]]:
    """
    Find nearby facilities using Google Places API (Nearby Search).

    Args:
        lat: Latitude of the current location.
        lon: Longitude of the current location.
        radius: Search radius in meters. Defaults to 5000.
        facility_type: Type of facility to search for. Defaults to "pharmacy".

    Returns:
        A list of nearby facilities with their display names and locations.
    """
    load_dotenv()
    api_url = "https://places.googleapis.com/v1/places:searchNearby"

    logger.info(
        f"Searching for {facility_type}s near lat={lat}, lon={lon}, radius={radius}m"
    )

    query_payload = {
        "includedTypes": [facility_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lon},
                "radius": radius,
            }
        },
    }

    api_key = os.getenv("PLACES_API_KEY")
    if not api_key:
        logger.error("PLACES_API_KEY environment variable not set")
        raise ValueError("PLACES_API_KEY environment variable not set")

    http_headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.location",
    }

    try:
        logger.debug(f"Making request to {api_url}")
        response = requests.post(
            api_url, json=query_payload, headers=http_headers, timeout=30
        )
        response.raise_for_status()

        places = response.json().get("places", [])
        logger.info(f"Found {len(places)} {facility_type}s nearby")
        return places

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching nearby facilities: {str(e)}")
        raise
