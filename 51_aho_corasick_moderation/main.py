from YoungLion import MultiPatternSearch
patterns=["free money","credential leak","spam link","api key","secret token"]
matcher=MultiPatternSearch(patterns)
messages=["normal conversation","possible API key was pasted here","free money spam link now"]
for text in messages:
    matches=matcher.find(text)
    print(text,[(m.pattern,m.start,m.end) for m in matches])
