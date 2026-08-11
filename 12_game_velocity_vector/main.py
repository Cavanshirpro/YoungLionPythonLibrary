from YoungLion import Vector

velocity = Vector([3, 4])
target = Vector([10, 0])
print("Speed:", velocity.magnitude())
print("Direction:", velocity.normalize().components)
print("Halfway velocity:", velocity.lerp(target, 0.5).components)
