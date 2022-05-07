
BLIZZARD_TOKENS_URL = "https://us.battle.net/oauth/token"

REINOS_BR = ["azralon", "nemesis", "goldrinn", "gallywix", "tol-barad"]

# API que provém os dados de PVP
PVP_RATING_API = (
    "https://us.api.blizzard.com/data/wow/pvp-season/${session}/pvp-leaderboard/${bracket}?"
    "namespace=dynamic-us&locale=en_US&access_token=${accessToken}"
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
ALL_CLASSES_API = (
    "https://us.api.blizzard.com/data/wow/playable-class/index?namespace=static-us&locale=en_US&access_token=${accessToken}"
)

# API que provém os ícones das classes
CLASS_MEDIA_API = (
    "https://us.api.blizzard.com/data/wow/media/playable-class/${class_id}?namespace=static-us&locale=en_US"
    "&access_token=${accessToken}"
)

# API que provém todas as specs
ALL_SPECS_API = (
    "https://us.api.blizzard.com/data/wow/playable-specialization/index?namespace=static-us&locale=en_US&access_token=${accessToken}"
)

# API que provém os ícones das specs das classes
SPEC_MEDIA_API = (
    "https://us.api.blizzard.com/data/wow/media/playable-specialization/${spec_id}?namespace=static-us&locale=en_US"
    "&access_token=${accessToken}"
)

# Configuração do tempo de timeout para as requisições (Em segundos)
TIMEOUT = 60

# Configuração do tempo de delay para aguardar entre as requisições, afim de não ser afetado pelo throttle
DELAY = 5

# Configuração do limite de requisições por segundo
REQUESTS_PER_SEC = 90
