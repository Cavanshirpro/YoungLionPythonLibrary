from YoungLion import Color

background = Color.from_hex("#202124")
foreground = Color.from_hex("#FFFFFF")
print("Contrast:", background.contrast_ratio(foreground))
print("Blend:", background.blend(foreground, 0.2).to_hex())
