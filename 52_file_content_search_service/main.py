from pathlib import Path
from tempfile import TemporaryDirectory
from YoungLion import FileSearchEngine
with TemporaryDirectory() as tmp:
    root=Path(tmp)
    (root/"ddm.md").write_text("DDM nested path indexes and batch operations",encoding="utf-8")
    (root/"release.txt").write_text("wheel build artifact release bundle",encoding="utf-8")
    (root/"notes.log").write_text("ordinary log entry",encoding="utf-8")
    engine=FileSearchEngine(root,content=True,extensions=[".md",".txt",".log"])
    for result in engine.search_results("nested index",limit=10):
        print(result.document.metadata["path"],round(result.score,3))
