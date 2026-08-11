from YoungLion import ListDDM
from models import Player

players = ListDDM(Player({"id": i, "wallet": 100 + i%500, "reputation": i%120, "active": i%7 != 0}) for i in range(10000))
before = players.sum("wallet")
plan = players.batch().multiply("wallet", 1.03).add("wallet", 15).clamp("wallet", 0, 2000).set("economy_version", 2)
changed = plan.execute(players)
after = players.sum("wallet")
print({"changed": changed, "before": round(before,2), "after": round(after,2), "mean": round(players.mean("wallet") or 0,2)})
