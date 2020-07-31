class CommunityModel:
    def __init__(self, data) -> None:
        self.name = data["name"]
        self.api_key = data["api_key"]
        self.owner_id = data["owner_id"]
        self.disabled = data["disabled"]
