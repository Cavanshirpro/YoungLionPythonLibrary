from YoungLion import Colors

styled = Colors.wrap("YoungLion", Colors.BOLD if hasattr(Colors, "BOLD") else Colors.BRIGHT, Colors.rgb(255, 180, 0))
print(styled)
print("Plain:", Colors.strip(styled))
print("Gradient:", Colors.gradient("native", (255, 80, 30), (80, 160, 255)))
