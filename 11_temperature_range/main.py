from YoungLion import Range

safe = Range(-20, 80)
reading = 95
print("Safe reading:", safe.clamp(reading))
print("Normalized 30C:", safe.normalize(30))
