from typing import List

from pydantic import BaseModel

# class Location(BaseModel):
#     """Location coordinates model.

#     Attributes:
#         latitude: The latitude coordinate
#         longitude: The longitude coordinate
#     """

#     latitude: float
#     longitude: float


class DisplayName(BaseModel):
    """Display name model for a place.

    Attributes:
        text: The display text of the place name
        languageCode: The language code of the text
    """

    text: str
    languageCode: str


class Place(BaseModel):
    """Model representing a place from the Places API.

    Attributes:
        location: The geographical location of the place
        displayName: The display name information of the place
    """

    id: str
    formattedAddress: str
    displayName: DisplayName


class PlacesResponse(BaseModel):
    """Model representing the complete Places API response.

    Attributes:
        places: List of places returned by the API
    """

    places: List[Place]
