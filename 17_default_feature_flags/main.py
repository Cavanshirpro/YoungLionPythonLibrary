from YoungLion import DefaultDDM

flags = DefaultDDM(
    {"search_v2": {"enabled": True, "rollout": 25}},
    default_factory=lambda: {"enabled": False, "rollout": 0},
)
print("existing:", flags.search_v2)
print("missing payments_v2:", flags.payments_v2)
flags.set_path("payments_v2.enabled", True)
print(flags.to_dict())
