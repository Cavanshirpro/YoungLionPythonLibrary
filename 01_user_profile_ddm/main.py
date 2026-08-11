from YoungLion import DDM

user = DDM({
    "id": 1001,
    "username": "cavan",
    "profile": {"name": "Cavan", "country": "AZ", "age": 18},
})
print("Username:", user.username)
print("Country:", user.get_path("profile.country"))
user.set_path("profile.age", 19)
print(user.to_json())
