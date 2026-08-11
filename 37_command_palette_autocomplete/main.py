from YoungLion import AutocompleteIndex

ac = AutocompleteIndex()
ac.add(("Open File", "open", 10.0))
ac.add(("Open Folder", "folder", 8.0))
ac.add(("Settings", "settings", 6.0))
print([(x.term, x.payload) for x in ac.suggest("ope")])
