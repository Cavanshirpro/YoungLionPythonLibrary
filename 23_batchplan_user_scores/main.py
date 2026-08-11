from YoungLion import ListDDM

users = ListDDM({"id": i, "score": i * 8, "active": False} for i in range(8))
plan = users.batch().add("score", 5).multiply("score", 1.1).clamp("score", 0, 50).set("active", True)
print("Changed:", plan.execute(users))
print(users.select("id", "score", "active") if hasattr(users, "select") else [u.to_dict() for u in users[:3]])
