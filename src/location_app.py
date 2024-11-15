import os
import requests
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

# Configure your Google Places API key
PLACES_API_KEY = "AIzaSyDvnQ8u9bvuulupuz9JkHXNEIJNSLeWzLQ"  # Replace with your actual API key

def find_nearby_pharmacies(lat, lon, radius=5000):
    """
    Find nearby pharmacies using Google Places API (Nearby Search).

    Args:
    - lat (float): Latitude of the current location.
    - lon (float): Longitude of the current location.
    - radius (int): Search radius in meters (default: 5000 meters).

    Returns:
    - list of pharmacies with details or an error message.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": PLACES_API_KEY,
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "pharmacy"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        try:
            # Try to parse JSON response
            response_json = response.json()
            return response_json.get("results", [])
        except ValueError:
            # Handle JSON decoding error
            return f"Error decoding JSON response: {response.text}"
    else:
        # Handle HTTP errors
        return f"Error: {response.status_code}, {response.text}"

# Streamlit UI
st.title("Find Nearby Pharmacies with Current Location")

# Get user location using browser's geolocation API
result = streamlit_js_eval(js_code="""
    new Promise((resolve, reject) => {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => resolve({lat: position.coords.latitude, lon: position.coords.longitude}),
                (error) => reject(error.message)
            );
        } else {
            reject('Geolocation is not supported by your browser.');
        }
    })
""")

if result and "lat" in result and "lon" in result:
    lat = result["lat"]
    lon = result["lon"]
    st.write(f"Your current location is Latitude: {lat}, Longitude: {lon}")

    # Call the function to find nearby pharmacies
    with st.spinner("Finding nearby pharmacies..."):
        pharmacies = find_nearby_pharmacies(lat, lon)

    if isinstance(pharmacies, list):
        if pharmacies:
            st.write("Nearby Pharmacies:")
            for pharmacy in pharmacies:
                st.write(f"Name: {pharmacy.get('name', 'N/A')}")
                st.write(f"Address: {pharmacy.get('vicinity', 'N/A')}")
                st.write("---")
        else:
            st.write("No nearby pharmacies found.")
    else:
        # Display error message if response is not a list
        st.write(pharmacies)
else:
    st.write("Unable to retrieve location. Please enable location access.")
