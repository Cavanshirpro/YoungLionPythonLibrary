from YoungLion import BM25Index, SearchDocument

index = BM25Index([
    SearchDocument(1, "Reset your password from account security settings"),
    SearchDocument(2, "Change application appearance and dark mode"),
    SearchDocument(3, "Recover a locked account using backup codes"),
])
for result in index.search("account recovery backup"):
    print(result.document.id, round(result.score, 3), result.document.text)
