from YoungLion import IdentityDDM

a = IdentityDDM({"user": 1, "state": "online"})
b = IdentityDDM({"user": 1, "state": "online"})
sessions = {a, b}
a.state = "away"
print("Session objects:", len(sessions))
