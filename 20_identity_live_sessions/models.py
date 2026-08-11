from YoungLion import IdentityDDM

class Session(IdentityDDM):
    def __init__(self, data):
        super().__init__(data)
        self.user_id = int(data.get("user_id", 0))
        self.state = str(data.get("state", "active"))
    def close(self): self.state = "closed"
