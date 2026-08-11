# Typed DDM subclass modeling

`DDM` can be used directly for completely dynamic data, but application code often benefits from a second layer: **typed domain subclasses**. This lets a project keep YoungLion's native-backed serialization, nested path operations and collection/search compatibility while also expressing domain invariants in normal Python classes.

## Core pattern

```python
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM

class Address(DDM):
    city: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.city = str(data.get("city", ""))
        self.country = str(data.get("country", ""))

class UserProfile(DDM):
    display_name: str
    age: int
    address: Address

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.display_name = str(data.get("display_name", "Unknown"))
        self.age = max(0, int(data.get("age", 0)))
        self.address = Address(data.get("address", {}))

class User(DDM):
    id: int
    username: str
    profile: UserProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get("id", 0))
        self.username = str(data.get("username", "unknown"))
        self.profile = UserProfile(data.get("profile", {}))
```

`super().__init__(data)` preserves all incoming keys. Assigning normalized fields afterwards replaces the raw values for the fields the model owns. In the example above the raw `profile` mapping becomes a `UserProfile`, and that profile's raw `address` mapping becomes an `Address`. `to_dict()` recursively serializes those nested DDM objects.

## Why this style works well

It gives you several layers at once:

1. **Dynamic compatibility.** Unknown fields can survive round trips because the base DDM initially keeps the supplied mapping.
2. **Typed known fields.** IDEs and type checkers understand the annotations you add to your subclass.
3. **Normalization.** `int(...)`, `str(...)`, enums, nested models and application validation can happen once at the model boundary.
4. **Native DDM operations.** The object is still a DDM, so `get_path`, `set_path`, `to_dict`, `to_json`, `diff`, `memory_info` and native collection/search features remain available.
5. **Domain behavior.** Methods such as `user.rename()`, `order.cancel()` or `account.can_withdraw()` can live next to the data they protect.

## Recommended constructor design

Keep constructors deterministic and cheap. Constructors are a good place for:

- type coercion;
- default values;
- nested DDM construction;
- local invariant checks;
- enum normalization;
- lightweight derived state.

Avoid doing network requests, database access or long-running work in `__init__`. Put those operations in a service/repository layer. This makes bulk loading and indexed searching much cheaper.

## Preserve unknown fields vs. strict models

Calling `super().__init__(data)` first means unknown keys stay in the DDM. That is often desirable for API responses and evolving schemas. If a project wants a strict outbound representation, provide an explicit method:

```python
class User(DDM):
    # ...
    def public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "username": self.username,
            "profile": self.profile.to_dict(),
        }
```

This keeps `DDM.to_dict()` lossless while giving the application a controlled public DTO.

## Alternate constructors

```python
class User(DDM):
    # normal __init__ omitted

    @classmethod
    def guest(cls, username: str = "guest") -> "User":
        return cls({
            "id": 0,
            "username": username,
            "profile": {"display_name": username, "age": 0, "address": {}},
        })
```

Alternate constructors are usually clearer than adding many flags to `__init__`.

## Validation methods

Validation can be strict at construction time or explicit:

```python
class BankAccount(DDM):
    balance: float

    def __init__(self, data):
        super().__init__(data)
        self.balance = float(data.get("balance", 0.0))
        if self.balance < 0:
            raise ValueError("balance cannot start negative")

    def withdraw(self, amount: float) -> None:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
```

For data-driven schema validation, `SchemaDDM` is also available. Subclass validation and `SchemaDDM` solve related but different problems: subclasses are excellent for application behavior; schema validation is useful when rules themselves are data.

## Clone behavior

Typed subclasses that follow the normal `__init__(data)` convention are reconstructed through their own constructor when `clone()` is called. This preserves nested domain types instead of turning them back into plain dictionaries:

```python
copy = user.clone()
assert isinstance(copy, User)
assert isinstance(copy.profile, UserProfile)
assert copy.profile is not user.profile
```

Built-in stateful variants (`FrozenDDM`, `SchemaDDM`, `DefaultDDM`, and `LazyDDM`) also preserve their variant-specific clone state in v0.1. Legacy subclasses with unusual constructor signatures retain a compatibility fallback, but new application models should prefer the one-mapping constructor pattern used throughout the examples branch.

## Nested-path search still works

```python
from YoungLion import ListDDM, DDMSearchEngine

users = ListDDM([
    User({"id": 1, "username": "alice", "profile": {"display_name": "Alice", "age": 24, "address": {"country": "US"}}}),
    User({"id": 2, "username": "cavan", "profile": {"display_name": "Cavan", "age": 18, "address": {"country": "AZ"}}}),
])

search = DDMSearchEngine(users).create_indexes(
    "profile.display_name",
    "profile.age",
    "profile.address.country",
)

azerbaijan = search.find("profile.address.country", "AZ")
adults = search.find("profile.age", 18, op="ge")
```

The index layer traverses DDM-compatible objects by path, so nested subclasses do not require a special search API.

## Bulk operations still work

```python
users.increment("profile.age", 1)
users.set_all("flags.migrated", True)
```

For arbitrary domain behavior, use a callback:

```python
def normalize_profile(profile: UserProfile) -> UserProfile:
    profile.display_name = profile.display_name.strip() or "Unknown"
    return profile

users.apply_path("profile", normalize_profile)
```

Callbacks run Python code, while path traversal remains delegated to YoungLion's collection layer. For pure numeric/set/clamp operations, prefer native bulk operations or `BatchPlan`.

## Inheritance beyond one level

Regular Python inheritance works. Keep the hierarchy meaningful:

```python
class Entity(DDM):
    id: int
    def __init__(self, data):
        super().__init__(data)
        self.id = int(data.get("id", 0))

class User(Entity):
    username: str
    def __init__(self, data):
        super().__init__(data)
        self.username = str(data.get("username", "unknown"))
```

Avoid deep inheritance trees built only to share fields. Composition with nested DDM models is usually easier to maintain.

## Typing notes

YoungLion ships `py.typed` and `.pyi` files for its public API. Your subclass annotations provide the application-specific part that no generic dynamic library can infer. A type checker can understand `user.profile.address.country` because those attributes are declared on your subclasses.

## Project layout

A larger application can use:

```text
app/
├── models/
│   ├── user.py
│   ├── order.py
│   └── product.py
├── repositories/
│   └── users.py
├── services/
│   └── user_service.py
└── main.py
```

Models should define structure and local behavior; repositories own collections/indexes/persistence; services coordinate use cases. The `examples` branch demonstrates this pattern in complete multi-file mini-projects.
