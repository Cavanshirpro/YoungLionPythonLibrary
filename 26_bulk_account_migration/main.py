from YoungLion import ListDDM
from models import User

users = ListDDM(User({"id": i, "score": i % 100, "active": True, "profile": {"name": f"User {i}", "country": "AZ" if i%2 else "US", "age": 18+i%40}, "legacy_rank": "member"}) for i in range(5000))
print("before columns:", users[0].to_dict())
users.rename_path("legacy_rank", "account.rank")
users.fill_missing("account.migrated", True)
users.copy_path("profile.country", "account.region")
print("after:", users[0].to_dict())
print("migrated:", users.count_path("account.migrated", True))
