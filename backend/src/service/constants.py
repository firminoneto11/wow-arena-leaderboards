from typing import Final
from pathlib import Path


# Endpoint to request access tokens
BLIZZARD_TOKENS_URL: Final[str] = "https://us.battle.net/oauth/token"

# Brazilian Realms
BRAZILIAN_REALMS: Final[str] = ["azralon", "nemesis", "goldrinn", "gallywix", "tol-barad"]

# Endpoint that provides the PVP Data
PVP_RATING_API: Final[str] = (
    "https://us.api.blizzard.com/data/wow/pvp-season/{session}/pvp-leaderboard/{bracket}?"
    "namespace=dynamic-us&locale=en_US&access_token={accessToken}"
)

# Endpoint that returns the character's profile data
PROFILE_API: Final[str] = (
    "https://us.api.blizzard.com/profile/wow/character/{realmSlug}/{charName}?namespace=profile-us&locale=en_US"
    "&access_token={accessToken}"
)

# Endpoint that returns the character's pictures
CHAR_MEDIA_API: Final[str] = (
    "https://us.api.blizzard.com/profile/wow/character/{realmSlug}/{charName}/character-media?namespace=profile-us"
    "&locale=en_US&access_token={accessToken}"
)

# Endpoint that returns all the data from wow classes
ALL_CLASSES_API: Final[
    str
] = "https://us.api.blizzard.com/data/wow/playable-class/index?namespace=static-us&locale=en_US&access_token={accessToken}"

# Endpoint that returns the icon for a wow class
CLASS_MEDIA_API: Final[str] = (
    "https://us.api.blizzard.com/data/wow/media/playable-class/{classId}?namespace=static-us&locale=en_US"
    "&access_token={accessToken}"
)

# Endpoint that returns all the data from specs
ALL_SPECS_API: Final[str] = (
    "https://us.api.blizzard.com/data/wow/playable-specialization/index?namespace=static-us&locale=en_US"
    "&access_token={accessToken}"
)

# Endpoint that returns the icon for a class spec
SPEC_MEDIA_API: Final[str] = (
    "https://us.api.blizzard.com/data/wow/media/playable-specialization/{specId}?namespace=static-us&locale=en_US"
    "&access_token={accessToken}"
)

# Timeout setting for the requests (In seconds)
TIMEOUT: Final[int] = 30

# Delay time between requests in order to not be affected by throttle
DELAY: Final[int] = 3

# Number of requests per second
REQUESTS_PER_SEC: Final[int] = 100

# Amount of time a HTTP request must be re-sent
MAX_RETRIES: Final[int] = 5

# Setting for the recurrence time of the fetching process (In seconds)
UPDATE_EVERY: Final[int] = 15

# Directory outside of src
BASE_DIR = Path(__file__).resolve().parent.parent.parent
