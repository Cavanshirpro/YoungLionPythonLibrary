from YoungLion import ApplicationSearch

search = ApplicationSearch()
search.add("appearance", "Appearance", "Light and dark mode", tags=["theme", "color"], fields={"section": "ui"}, payload="/settings/appearance")
search.add("privacy", "Privacy", "Permissions and telemetry", tags=["security"], fields={"section": "account"}, payload="/settings/privacy")
print(search.search("apperance"))
