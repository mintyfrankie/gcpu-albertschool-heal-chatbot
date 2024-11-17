from urllib.parse import urlencode
import requests


def get_doctors(
    specializations: list[str],
    latitude: float,
    longitude: float,
    is_urgent: bool = False,
) -> list:
    """
    Fetches doctors from Doctolib API with the given specializations.

    Args:
        specializations (list[str]): The specializations of the doctors to fetch.
        latitude (float): The latitude of the location to search for doctors.
        longitude (float): The longitude of the location to search for doctors.
        is_urgent (bool, optional): Whether to search for urgent doctors or not. Defaults to False.

    Returns:
        list: A list of doctor objects as returned by the Doctolib API.

    Raises:
        requests.exceptions.RequestException: If the request to the Doctolib API fails.
    """
    page_number = 1
    doctor_list = []

    specializations = specializations[:3]

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

        response = requests.get(api_url, headers=headers, params=query_params)
        response.raise_for_status()

        doctor_list.extend(response.json().get("data", {}).get("doctors", [])[:5])

    return doctor_list
