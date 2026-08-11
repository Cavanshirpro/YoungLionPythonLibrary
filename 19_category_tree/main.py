from YoungLion import TreeDDM

root = TreeDDM("Store")
electronics = root.add_child("Electronics")
electronics.add_child("Laptops")
electronics.add_child("Phones")
root.add_child("Books")
print([node.value for node in root.walk("dfs")])
print("Depth:", root.depth(), "Nodes:", root.size())
