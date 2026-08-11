from YoungLion import DDM

settings = DDM({"ui": {"theme": "dark", "scale": 1.0}, "audio": {"volume": 70}})
before = settings.clone()
settings.set_path("ui.scale", 1.25)
settings.set_path("audio.volume", 80)
print("Changed:", before.diff(settings))
