from YoungLion import ApplicationSearch

search = ApplicationSearch()
for pid, title, category in [(1, "Gaming Laptop", "computer"), (2, "Office Laptop", "computer"), (3, "Wireless Mouse", "accessory")]:
    search.add(pid, title, fields={"category": category}, payload={"id": pid, "title": title})
print(search.search("laptpo"))
print("Facets:", search.facet("category"))
