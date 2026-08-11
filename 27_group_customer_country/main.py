from YoungLion import ListDDM

customers = ListDDM([
    {"name": "A", "profile": {"country": "AZ"}},
    {"name": "B", "profile": {"country": "TR"}},
    {"name": "C", "profile": {"country": "AZ"}},
])
print(customers.count_by("profile.country"))
print(customers.distinct("profile.country"))
