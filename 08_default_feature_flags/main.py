from YoungLion import DefaultDDM

flags = DefaultDDM({"new_ui": True}, default_factory=lambda: False)
print("new_ui:", flags["new_ui"])
print("beta_search:", flags["beta_search"])
