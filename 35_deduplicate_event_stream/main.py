from YoungLion import ListDDM
from models import Event

rows = ListDDM(Event({"id":i,"event_id":f"evt-{i//2}","type":"click" if i%3 else "view"}) for i in range(100))
unique = rows.deduplicate("event_id")
print("before:", len(rows), "after:", len(unique))
print([e.event_id for e in unique[:8]])
