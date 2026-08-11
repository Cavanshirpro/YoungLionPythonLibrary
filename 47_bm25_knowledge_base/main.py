from YoungLion import BM25Index, SearchDocument
articles=[
    SearchDocument("ddm","DDM collections use native path operations for bulk structured data",fields={"topic":"data"}),
    SearchDocument("search","DDMSearchEngine builds reusable nested indexes and supports exact range and fuzzy text queries",fields={"topic":"search"}),
    SearchDocument("file","File provides atomic JSON text binary checksum backup and structured format helpers",fields={"topic":"file"}),
]
index=BM25Index(articles)
for result in index.search("nested DDM search index",limit=3):
    print(result.document.id, round(result.score,3), result.document.text)
print(index.stats())
