from YoungLion import NumericSearch

prices = NumericSearch([(19.99, "mouse"), (49.0, "keyboard"), (99.0, "headset"), (899.0, "laptop")])
print("30-120:", prices.range(30, 120))
print("Nearest 55:", prices.nearest(55, 2))
