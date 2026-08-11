from pathlib import Path
from YoungLion import File

f = File(str(Path(__file__).parent / "workspace"))
f.csv_write("customers.csv", [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
f.csv_append("customers.csv", [{"id": "3", "name": "Cavan"}])
f.csv_update("customers.csv", [{"id": "2", "name": "Robert"}], identifier="id")
print(f.csv_read("customers.csv"))
