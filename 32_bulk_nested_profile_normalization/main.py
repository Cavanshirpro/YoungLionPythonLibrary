from YoungLion import ListDDM
from models import User, Profile

users = ListDDM(User({"id":i,"score":i,"active":True,"profile":{"name":f"  User {i}  ","country":"az" if i%2 else "US","age":18+i%10}}) for i in range(1000))
def normalize(profile: Profile) -> Profile:
    profile.name = profile.name.strip()
    profile.country = profile.country.upper()
    return profile

updated = users.apply_path("profile", normalize)
print("updated:", len(updated))
print(users[1].profile.to_dict())
