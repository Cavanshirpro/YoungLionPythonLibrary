from YoungLion import EventBus

bus = EventBus()
steps = []
bus.subscribe("order.created", lambda order_id: steps.append(("audit", order_id)), priority=10)
bus.once("order.created", lambda order_id: steps.append(("welcome", order_id)), priority=5)
bus.emit("order.created", "ORD-1")
bus.emit("order.created", "ORD-2")
print(steps)
