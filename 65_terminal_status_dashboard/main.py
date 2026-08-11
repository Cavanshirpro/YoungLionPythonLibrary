from YoungLion import Terminal

rows = [["database", "ok", "12 ms"], ["search", "ok", "4 ms"], ["backup", "running", "-"]]
print(Terminal.table(rows, headers=["Service", "State", "Latency"]))
print(Terminal.progress(72, 100, label="Release"))
