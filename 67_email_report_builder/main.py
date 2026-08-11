from YoungLion import EmailManager

mail = EmailManager("smtp.example.invalid", 587, "bot@example.invalid", "not-a-real-password")
message = mail.build_email(
    "owner@example.invalid",
    "Daily report",
    "All services are healthy.",
    html="<b>All services are healthy.</b>",
)
print(message["Subject"])
print(message.get_content_type())
