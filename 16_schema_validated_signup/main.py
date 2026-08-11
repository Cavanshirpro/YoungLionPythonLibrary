from models import User, validate_signup

raw = {"username": " Cavan ", "age": 18, "email": "CAVAN@example.test"}
validated = validate_signup(raw)
user = User(validated)
print(user.to_dict())
print(user.username, user.email)
