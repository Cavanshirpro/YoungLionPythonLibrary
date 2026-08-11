from pathlib import Path
from YoungLion import File

f = File(str(Path(__file__).parent / "workspace"))
f.xml_write("order.xml", {"id": "ORD-1", "customer": {"name": "Alice"}}, root_element="order")
print(f.xml_read("order.xml"))
