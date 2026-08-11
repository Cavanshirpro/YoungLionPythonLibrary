from YoungLion import ApplicationSearch
articles=[("install","Installing YoungLion","Build from PyPI or source with a C++17 compiler","setup"),("ddm","Modeling data with DDM","Typed subclasses nested models and dynamic fields","data"),("search","Searching DDM collections","Exact range fuzzy and composite indexes","search"),("files","Working with File","Atomic JSON backups checksums and formats","files")]
app=ApplicationSearch()
for id,title,body,cat in articles: app.add(id,title=title,body=body,fields={"category":cat},payload={"id":id,"title":title,"category":cat})
print(app.search("nested model"))
print("all facets:",app.facet("category"))
print("query facets:",app.facet("category",query="search index"))
