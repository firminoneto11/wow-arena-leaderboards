# Endpoint to request access tokens
BLIZZARD_TOKENS_URL = "https://us.battle.net/oauth/token"

# Brazilian Realms
BRAZILIAN_REALMS = ["azralon", "nemesis", "goldrinn", "gallywix", "tol-barad"]

# Endpoint that provides the PVP Data
PVP_RATING_API = (
    "https://us.api.blizzard.com/data/wow/pvp-season/{session}/pvp-leaderboard/{bracket}?"
    "namespace=dynamic-us&locale=en_US&access_token={accessToken}"
)

# API que provém os dados do perfil personagem
PROFILE_API = (
    "https://us.api.blizzard.com/profile/wow/character/${realm_slug}/${char_name}?namespace=profile-us&locale=en_US"
    "&access_token=${accessToken}"
)

# API que provém as imagens dos personagens
CHAR_MEDIA_API = (
    "https://us.api.blizzard.com/profile/wow/character/${realm_slug}/${char_name}/character-media?namespace=profile-us"
    "&locale=en_US&access_token=${accessToken}"
)

# API que provém todas as classes
ALL_CLASSES_API = "https://us.api.blizzard.com/data/wow/playable-class/index?namespace=static-us&locale=en_US&access_token=${accessToken}"

# API que provém os ícones das classes
CLASS_MEDIA_API = (
    "https://us.api.blizzard.com/data/wow/media/playable-class/${class_id}?namespace=static-us&locale=en_US"
    "&access_token=${accessToken}"
)

# API que provém todas as specs
ALL_SPECS_API = "https://us.api.blizzard.com/data/wow/playable-specialization/index?namespace=static-us&locale=en_US&access_token=${accessToken}"

# API que provém os ícones das specs das classes
SPEC_MEDIA_API = (
    "https://us.api.blizzard.com/data/wow/media/playable-specialization/${spec_id}?namespace=static-us&locale=en_US"
    "&access_token=${accessToken}"
)

# Timeout setting for the requests (In seconds)
TIMEOUT = 30

# Delay time between requests in order to not be affected by throttle
DELAY = 3

# Number of requests per second
REQUESTS_PER_SEC = 100

# Amount of time a HTTP request must be re-sent
MAX_RETRIES = 5

# Setting for the recurrence time of the fetching process (In seconds)
UPDATE_EVERY = 10
