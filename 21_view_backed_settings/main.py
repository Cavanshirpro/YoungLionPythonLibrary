from YoungLion import ViewDDM

raw = {"theme": "dark", "window": {"width": 1280, "height": 720}}
view = ViewDDM(raw)
view["theme"] = "light"
view.set_path("window.width", 1440)
print("view:", view.to_dict())
print("same backing mapping:", raw)
