import http.client
import json
import os

import requests
import streamlit as st


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

    response = requests.post(api_url, json=query_payload, headers=http_headers, timeout=30)

    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

    return response.json().get("places", [])


#     """
#     Find nearby facilities using Google Places API (Nearby Search).

#     Args:
#     - lat (float): Latitude of the current location.
#     - lon (float): Longitude of the current location.
#     - radius (int): Search radius in meters (default: 5000 meters).

#     Returns:
#     - list of facilities with details or an error message.
#     """
#     base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
#     params = {
#         "key": os.getenv("PLACES_API_KEY"),
#         "location": f"{lat},{lon}",
#         "radius": radius,
#         "type": facility_type,
#     }
#     response = requests.get(base_url, params=params)
#     if response.status_code == 200:
#         try:
#             # Try to parse JSON response
#             response_json = response.json()
#             return response_json.get("results", [])
#         except ValueError:
#             # Handle JSON decoding error
#             return f"Error decoding JSON response: {response.text}"
#     else:
#         # Handle HTTP errors
#         return f"Error: {response.status_code}, {response.text}"


# # Streamlit UI
# st.title("Find Nearby Pharmacies")

# # Example for getting latitude and longitude (this should be replaced with user's actual location)
# lat = st.number_input("Enter your latitude:", value=0.0, format="%.6f")
# lon = st.number_input("Enter your longitude:", value=0.0, format="%.6f")

# if lat != 0.0 and lon != 0.0:
#     with st.spinner("Finding nearby pharmacies..."):
#         pharmacies = find_nearby_facilities(lat, lon)

#     if isinstance(pharmacies, list):
#         if pharmacies:
#             st.write("Nearby Pharmacies:")
#             for pharmacy in pharmacies:
#                 name = pharmacy.get("name", "N/A")
#                 address = pharmacy.get("vicinity", "N/A")
#                 place_lat = pharmacy["geometry"]["location"]["lat"]
#                 place_lon = pharmacy["geometry"]["location"]["lng"]
#                 # Creating a Google Maps link
#                 maps_link = f"https://www.google.com/maps/search/?api=1&query={place_lat},{place_lon}"

#                 st.write(f"Name: {name}")
#                 st.write(f"Address: {address}")
#                 st.write(f"[Get Directions]({maps_link})")
#                 st.write("---")
#         else:
#             st.write("No nearby pharmacies found.")
#     else:
#         # Display error message if response is not a list
#         st.write(pharmacies)
