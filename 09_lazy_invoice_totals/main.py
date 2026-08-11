from YoungLion import LazyDDM

invoice = LazyDDM(
    {"lines": [{"qty": 2, "price": 10}, {"qty": 1, "price": 15}]},
    lazy={"total": lambda d: sum(x["qty"] * x["price"] for x in d.lines)},
)
print("Total:", invoice.total)
invoice.lines.append({"qty": 3, "price": 5})
invoice.invalidate("total")
print("New total:", invoice.total)
