class SteamSettings:
    def __init__(self, api_key: str,
                 api_url: str = "https://api.steampowered.com/") -> None:
        self._api_key = api_key
        self._api_url = api_url
