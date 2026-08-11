from YoungLion import DDMBuilder

request = (DDMBuilder()
    .set("id", "req-1")
    .nest("profile", lambda b: b.set("name", "Cavan").set("tier", "pro"))
    .add_list("scopes", ["read", "write"])
    .build())
print(request.to_dict())
