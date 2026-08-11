from YoungLion import ListDDM

rows = ListDDM([{"user": {"name": "A"}}, {"user": {"name": "B"}}])
rows.copy_path("user.name", "display_name")
rows.rename_path("user.name", "user.full_name")
print([r.to_dict() for r in rows])
