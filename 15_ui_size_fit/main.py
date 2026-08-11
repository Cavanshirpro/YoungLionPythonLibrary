from YoungLion import Size

image = Size(1920, 1080)
viewport = Size(800, 600)
fitted = image.fit_inside(viewport)
print(f"{fitted.width:.0f}x{fitted.height:.0f}")
