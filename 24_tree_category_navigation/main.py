from YoungLion import TreeDDM

root = TreeDDM("products")
electronics = root.add_child(TreeDDM("electronics"))
electronics.add_child(TreeDDM("laptops"))
electronics.add_child(TreeDDM("keyboards"))
root.add_child(TreeDDM("books"))
print(root)
print("children:", [child.value for child in root.children])
