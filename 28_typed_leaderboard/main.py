from YoungLion import ListDDM
from models import Player

players = ListDDM(Player({"id":i,"name":f"P{i}","score":(i*37)%1000,"team":"lion" if i%3==0 else "wolf"}) for i in range(1000))
players.sort_by("score", reverse=True, inplace=True)
print("top 5:", [(p.name,p.score) for p in players.take(5)])
median_score = players.nth("score", len(players)//2)
print("median candidate:", median_score)
print("lion top:", [(p.name,p.score) for p in ListDDM(players.filter_path("team","lion")).top("score",5)])
