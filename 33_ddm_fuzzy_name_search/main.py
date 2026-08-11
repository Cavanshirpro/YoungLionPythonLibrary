from YoungLion import ListDDM, DDMSearchEngine

users = ListDDM([{"profile": {"name": n}} for n in ["Alexander", "Alexandra", "Alexa", "Bob"]])
engine = DDMSearchEngine(users)
engine.create_index("profile.name")
hits = engine.text("profile.name", "Aleksander", hits=True)
print([(h.value, round(h.score, 3)) for h in hits[:3]])
