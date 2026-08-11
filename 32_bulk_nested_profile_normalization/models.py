from YoungLion import DDM

class Profile(DDM):
    name: str
    country: str
    age: int
    def __init__(self, data):
        super().__init__(data)
        self.name = str(data.get("name", "Unknown"))
        self.country = str(data.get("country", "Unknown"))
        self.age = int(data.get("age", 0))

class User(DDM):
    id: int
    score: float
    active: bool
    profile: Profile
    def __init__(self, data):
        super().__init__(data)
        self.id = int(data.get("id", 0))
        self.score = float(data.get("score", 0))
        self.active = bool(data.get("active", True))
        self.profile = Profile(data.get("profile", {}))
