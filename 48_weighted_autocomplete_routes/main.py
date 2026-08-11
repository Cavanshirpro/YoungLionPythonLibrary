from YoungLion import AutocompleteIndex, AutocompleteEntry
index=AutocompleteIndex([
    AutocompleteEntry("Open Project", {"route":"/open"}, 10),
    AutocompleteEntry("Open Recent", {"route":"/recent"}, 8),
    AutocompleteEntry("Open Settings", {"route":"/settings"}, 4),
    AutocompleteEntry("Optimize Database", {"route":"/db/optimize"}, 3),
])
for prefix in ["op","open p","optmize"]:
    print(prefix,[(x.term,x.weight,x.payload) for x in index.suggest(prefix,limit=4,min_score=0.5)])
