from YoungLion import Vector, Point, Size, Matrix, Color

velocity = Vector([3, 4, 0])
position = Point(120, 80)
viewport = Size(1920, 1080)
transform = Matrix([[1, 0, 20], [0, 1, 10], [0, 0, 1]])
accent = Color(255, 180, 20)
print("speed:", velocity.magnitude())
print("position:", position)
print("viewport:", viewport)
print("transform:", transform)
print("accent:", accent)
