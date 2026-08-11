from YoungLion import ViewDDM

raw = {"database": {"host": "localhost"}, "debug": False}
view = ViewDDM(raw)
view.set_path("database.host", "db.internal")
view["debug"] = True
print("Original dict changed:", raw)
