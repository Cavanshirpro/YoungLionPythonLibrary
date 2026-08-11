from YoungLion import DDM

state = DDM({"session": {"id": "abc"}, "items": [1, 2, 3]})
encoded = state.to_json(indent=2)
restored = DDM.from_json(encoded)
print(restored.to_dict())
