from YoungLion import ListDDM, DDM

rows = ListDDM(DDM({"id":i,"profile":{"full_name":f"User {i}","old_country":"AZ"},"legacy":{"enabled":True}}) for i in range(2500))
rows.rename_path("profile.full_name","profile.display_name")
rows.move_path("profile.old_country","profile.country")
rows.delete_path("legacy")
rows.fill_missing("schema_version",2)
print(rows[0].to_dict())
print("v2:", rows.count_path("schema_version",2))
