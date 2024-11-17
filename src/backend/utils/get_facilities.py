import os

import requests

from dotenv import load_dotenv


def find_nearby_facilities(
    lat: float,
    lon: float,
    radius: int = 5000,
    facility_type: str = "pharmacy",
) -> list:
    """
    Find nearby facilities using Google Places API (Nearby Search).

    Args:
        lat (float): Latitude of the current location.
        lon (float): Longitude of the current location.
        radius (int): Search radius in meters. Defaults to 5000.
        facility_type (str): Type of facility to search for. Defaults to "pharmacy".

    Returns:
        list: A list of nearby facilities with their display names and locations.
    """

    load_dotenv()
    api_url = "https://places.googleapis.com/v1/places:searchNearby"

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

    http_headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("PLACES_API_KEY"),
        "X-Goog-FieldMask": "places.displayName,places.location",
    }

    response = requests.post(
        api_url, json=query_payload, headers=http_headers, timeout=30
    )

    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

    return response.json().get("places", [])
