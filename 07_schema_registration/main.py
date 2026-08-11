from YoungLion import SchemaDDM

schema = {"name": str, "age": int, "active": bool}
user = SchemaDDM({"name": "Aylin", "age": 22, "active": True}, schema)
user.set_validated("age", 23)
print(user.to_dict())
