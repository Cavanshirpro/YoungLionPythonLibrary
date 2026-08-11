from YoungLion import SetDDM
from models import Account

accounts = SetDDM(key_path="id")
for row in [{"id":1,"email":"a@test","score":10},{"id":2,"email":"b@test","score":20},{"id":1,"email":"duplicate@test","score":99}]:
    print("added", row["id"], accounts.add(Account(row)))
print("count:", len(accounts))
accounts.increment("score", 5)
print([a.to_dict() for a in accounts])
