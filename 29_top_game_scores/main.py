from YoungLion import ListDDM

players = ListDDM({"name": f"P{i}", "score": (i * 17) % 101} for i in range(12))
print("Top 3:", [(p.name, p.score) for p in players.top("score", 3)])
print("Average:", players.mean("score"))
