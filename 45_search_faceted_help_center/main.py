from YoungLion import ApplicationSearch

help_search = ApplicationSearch()
help_search.add(1, "Reset password", fields={"category": "account"}, payload="article-1")
help_search.add(2, "Change password", fields={"category": "account"}, payload="article-2")
help_search.add(3, "Export files", fields={"category": "files"}, payload="article-3")
print(help_search.facet("category"))
print(help_search.search("password"))
