from urllib.parse import urlencode
import requests
from typing import List, Dict, Any

from backend.utils.logging import setup_logger

logger = setup_logger(__name__)


def get_doctors(
    specializations: List[str],
    latitude: float,
    longitude: float,
    is_urgent: bool = False,
) -> List[Dict[str, Any]]:
    """
    Fetches doctors from Doctolib API with the given specializations.

    Args:
        specializations: The specializations of the doctors to fetch.
        latitude: The latitude of the location to search for doctors.
        longitude: The longitude of the location to search for doctors.
        is_urgent: Whether to search for urgent doctors or not. Defaults to False.

    Returns:
        A list of doctor objects as returned by the Doctolib API.

    Raises:
        requests.exceptions.RequestException: If the request to the Doctolib API fails.
    """
    page_number = 1
    doctor_list = []

    specializations = specializations[:3]
    logger.info(f"Searching for doctors with specializations: {specializations}")
    logger.info(f"Location: lat={latitude}, lon={longitude}, urgent={is_urgent}")

    for specialization in specializations:
        api_url = f"https://www.doctolib.fr/{specialization}/"
        query_params = {
            "latitude": latitude,
            "longitude": longitude,
            "page": page_number,
        }
        if is_urgent:
            query_params["ref_visit_motive_id"] = 116

        headers = {
            "accept": "application/json, application/json",
            "content-type": "application/json; charset=utf-8",
            "priority": "u=1, i",
            "referer": f"{api_url}?{urlencode(query_params)}",
        }

        logger.debug(f"Making request to {api_url} with params: {query_params}")

        try:
            response = requests.get(api_url, headers=headers, params=query_params)
            response.raise_for_status()

            doctors = response.json().get("data", {}).get("doctors", [])[:5]
            logger.info(
                f"Found {len(doctors)} doctors for specialization {specialization}"
            )
            doctor_list.extend(doctors)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching doctors for {specialization}: {str(e)}")
            raise

    logger.info(f"Total doctors found: {len(doctor_list)}")
    return doctor_list
