from YoungLion import MultiPatternSearch

matcher = MultiPatternSearch(["secret", "token", "password"], case_sensitive=False)
text = "Never paste your PASSWORD or access token into a public issue."
print([(m.pattern, m.start, m.end) for m in matcher.find(text)])
