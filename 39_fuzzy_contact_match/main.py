from YoungLion import FuzzyMatcher

query = "Cavansir"
for candidate in ["Cavanşir", "Javanshir", "Cavan", "Alice"]:
    print(candidate, round(FuzzyMatcher.hybrid(query, candidate), 3))
