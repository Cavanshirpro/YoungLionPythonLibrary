from YoungLion import DDMBuilder

request = (
    DDMBuilder()
    .set("id", "job-42")
    .nest("profile", lambda b: b.set("name", "Cavan").set("country", "AZ"))
    .nest("options", lambda b: b.set("priority", 5).set("dry_run", True))
    .build()
)
print(request.to_json())
print("country:", request.get_path("profile.country"))
