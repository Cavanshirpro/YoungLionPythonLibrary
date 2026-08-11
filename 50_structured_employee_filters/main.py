from YoungLion import StructuredSearch
rows=[
 {"id":1,"name":"Alice","department":"engineering","age":30,"active":True},
 {"id":2,"name":"Cavan","department":"engineering","age":18,"active":True},
 {"id":3,"name":"Bob","department":"sales","age":44,"active":False},
]
search=StructuredSearch(rows, field_weights={"name":2.0,"department":1.5})
results=search.search("engineering", filters={"department":"engineering","active":True}, limit=10)
print([r.document.metadata["record"] for r in results])
