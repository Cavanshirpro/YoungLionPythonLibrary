from YoungLion import LazyDDM

invoice = LazyDDM(
    {"subtotal": 199.0, "tax_rate": 0.18, "shipping": 12.0},
    lazy={
        "tax": lambda d: round(d.subtotal * d.tax_rate, 2),
        "total": lambda d: round(d.subtotal + d.tax + d.shipping, 2),
    },
)
print("raw keys before access:", list(invoice.keys()))
print("total:", invoice.total)
print("serialized:", invoice.to_dict())
invoice.invalidate("tax", "total")
print("recomputed:", invoice.total)
