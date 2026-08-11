from YoungLion import Timeline

tl = Timeline(0, 100)
tl.add_event(0, "planning")
tl.add_event(40, "feature-freeze")
tl.add_event(80, "rc")
tl.add_event(100, "release")
print("Progress at day 65:", tl.get_progress(65))
print("Middle events:", tl.events_between(30, 90))
