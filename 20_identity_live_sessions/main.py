from models import Session

a = Session({"user_id": 1, "state": "active"})
b = Session({"user_id": 1, "state": "active"})
sessions = {a, b}
print("distinct live objects:", len(sessions))
a.close()
print(a.state, b.state)
