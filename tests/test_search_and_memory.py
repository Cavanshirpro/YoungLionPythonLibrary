from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from YoungLion import DDM, File
from YoungLion.search import (
    BM25Index,
    FileSearchEngine,
    FuzzyMatcher,
    NumericSearch,
    SearchAlgorithm,
    SearchDocument,
    SearchIndex,
    StructuredSearch,
)


def test_ddm_single_storage_and_memory_reduction():
    data = {f"field_{i}": i for i in range(100)}
    model = DDM(data)
    assert model._data is model.__dict__
    assert "_data" not in model.__dict__
    assert model.field_5 == 5
    model.field_5 = 7
    assert model._data["field_5"] == 7
    info = model.memory_info()
    assert info["keys"] == 100
    assert info["recursive_bytes"] >= info["storage_bytes"]

    class Legacy:
        def __init__(self, raw):
            self._data = dict(raw)
            for key, value in raw.items():
                setattr(self, key, value)

    legacy = Legacy(data)
    new_shallow = sys.getsizeof(model) + sys.getsizeof(model.__dict__)
    old_shallow = sys.getsizeof(legacy) + sys.getsizeof(legacy.__dict__) + sys.getsizeof(legacy._data)
    assert new_shallow < old_shallow


def test_native_fuzzy_algorithms_unicode_and_transposition():
    assert FuzzyMatcher.levenshtein("kitten", "sitting") == 3
    assert FuzzyMatcher.damerau_levenshtein("ca", "ac") == 1
    assert FuzzyMatcher.jaro_winkler("MARTHA", "MARHTA") > 0.95
    assert FuzzyMatcher.trigram("Azərbaycan", "Azerbaycan") > 0.25
    assert FuzzyMatcher.hybrid("mentalist", "mentalsit") > 0.80


def test_hybrid_and_bm25_search():
    docs = [
        SearchDocument(1, "The Mentalist detective Patrick Jane solves crimes", {"kind": "tv"}),
        SearchDocument(2, "Fast native C++ file operations and filesystem utilities", {"kind": "code"}),
        SearchDocument(3, "Sherlock Holmes detective mystery investigation", {"kind": "tv"}),
    ]
    index = SearchIndex(docs)
    fuzzy = index.search("mentalsit", min_score=0.1)
    assert fuzzy and fuzzy[0].document.id == 1
    filtered = index.search("detective", filters={"kind": "tv"})
    assert filtered and all(r.document.metadata["kind"] == "tv" for r in filtered)
    bm25 = BM25Index(docs).search("native filesystem")
    assert bm25 and bm25[0].document.id == 2
    substring = index.search("Patrick", algorithm=SearchAlgorithm.SUBSTRING)
    assert substring and substring[0].positions


def test_structured_numeric_and_file_search():
    structured = StructuredSearch(
        [
            {"id": "a", "name": "YoungLion", "category": "python", "description": "native C++ library"},
            {"id": "b", "name": "Other", "category": "game", "description": "card game"},
        ],
        field_weights={"name": 2.0, "description": 1.5},
    )
    assert structured.search("native library")[0].document.id == "a"

    numbers = NumericSearch([(10, "ten"), (20, "twenty"), (30, "thirty")])
    assert numbers.nearest(22, 1)[0][1] == "twenty"
    assert [v for v, _ in numbers.range(10, 20)] == [10.0, 20.0]

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "alpha.txt").write_text("dynamic data model native search", encoding="utf-8")
        (root / "beta.md").write_text("completely unrelated", encoding="utf-8")
        engine = FileSearchEngine(root, content=True)
        results = engine.search_results("dynamic data", extension="txt")
        assert results and results[0].document.fields["name"] == "alpha.txt"


def test_extended_file_api():
    with tempfile.TemporaryDirectory() as td:
        f = File(td)
        f.write_bytes("blob.bin", b"abc\x00def")
        assert f.read_bytes("blob.bin") == b"abc\x00def"
        assert f.file_size("blob.bin") == 7
        assert len(f.checksum("blob.bin", "crc32")) == 8
        assert len(f.checksum("blob.bin", "sha256")) == 64
        f.write_bytes("blob-copy.bin", b"abc\x00def")
        assert f.compare_files("blob.bin", "blob-copy.bin")
        assert f.touch("empty.txt")
        f.atomic_write_text("atomic.txt", "one\ntwo\nthree\n")
        assert f.line_count("atomic.txt") == 3
        assert f.head("atomic.txt", 2) == ["one", "two"]
        assert f.tail("atomic.txt", 2) == ["two", "three"]
        f.atomic_write_json("atomic.json", {"ok": True})
        assert f.json_read("atomic.json") == {"ok": True}
        assert f.directory_size() >= 7


def test_inverted_index_autocomplete_and_query_object():
    from YoungLion.search import AutocompleteIndex, InvertedIndex, SearchQuery

    inverted = InvertedIndex()
    inverted.add("a", ["native", "search", "search"])
    inverted.add("b", ["python", "search"])
    assert inverted.document_count == 2
    assert inverted.token_count == 5
    assert inverted.postings("search")[0].term_frequency in {1, 2}
    ranked = inverted.bm25(["native"])
    assert list(ranked) == ["a"]

    autocomplete = AutocompleteIndex([
        ("YoungLion", "project", 5.0),
        ("young developer", "person", 2.0),
        ("Python", "language", 3.0),
    ])
    suggestions = autocomplete.suggest("you")
    assert [item.payload for item in suggestions[:2]] == ["project", "person"]
    fuzzy = autocomplete.suggest("YungLion")
    assert fuzzy and fuzzy[0].payload == "project"

    index = SearchIndex([SearchDocument(1, "native C++ search"), SearchDocument(2, "card game")])
    results = index.search(SearchQuery("native", SearchAlgorithm.BM25, limit=1))
    assert results and results[0].document.id == 1


def test_multi_pattern_aho_corasick_and_duplicate_numeric_values():
    from YoungLion.search import MultiPatternSearch

    matcher = MultiPatternSearch(["he", "she", "his", "hers"])
    matches = matcher.find("ushers")
    found = {(match.pattern, match.start, match.end) for match in matches}
    assert ("she", 1, 4) in found
    assert ("he", 2, 4) in found
    assert ("hers", 2, 6) in found
    assert matcher.contains_any("SHE")

    # Equal numeric keys used to make tuple insertion compare payload objects.
    class Payload:
        pass

    numbers = NumericSearch()
    first, second = Payload(), Payload()
    numbers.add(10, first)
    numbers.add(10, second)
    assert len(numbers.range(10, 10)) == 2


def test_file_atomic_binary_find_and_chunks():
    with tempfile.TemporaryDirectory() as td:
        f = File(td)
        f.atomic_write_bytes("nested/blob.bin", b"abcdefghij")
        assert f.read_bytes("nested/blob.bin") == b"abcdefghij"
        chunks = list(f.read_chunks("nested/blob.bin", 4))
        assert chunks == [b"abcd", b"efgh", b"ij"]
        f.txt_write_str("nested/a.txt", "hello")
        f.txt_write_str("nested/b.log", "hello")
        found = f.find_files("*.txt", "nested")
        assert len(found) == 1 and found[0].endswith("a.txt")


def test_multitoken_prefix_scoring_and_sorted_prefix_cache():
    from YoungLion.search import InvertedIndex, SearchAlgorithm, SearchIndex

    index = SearchIndex([
        {"id": 1, "text": "alpha beta gamma"},
        {"id": 2, "text": "alphabet betamax"},
        {"id": 3, "text": "alpha delta"},
    ])
    result_ids = [r.document.id for r in index.search("alp bet", algorithm=SearchAlgorithm.PREFIX, limit=None)]
    assert result_ids[:2] == [1, 2]
    results = index.search("alp bet", algorithm=SearchAlgorithm.PREFIX, limit=None)
    assert results[0].score == results[1].score == 0.85
    assert results[2].document.id == 3 and results[2].score == 0.425

    inv = InvertedIndex()
    inv.add("a", ["zulu", "alpha", "alpine", "beta"])
    assert inv.prefix_terms("al") == ["alpha", "alpine"]
    # Mutating the index must invalidate the sorted vocabulary cache.
    inv.add("b", ["albatross"])
    assert inv.prefix_terms("al") == ["albatross", "alpha", "alpine"]


def test_prefix_search_does_not_drop_terms_after_vocabulary_limit():
    from YoungLion.search import SearchAlgorithm, SearchIndex

    docs = [{"id": i, "text": f"application{i:02d}"} for i in range(64)]
    index = SearchIndex(docs)
    results = index.search("app", algorithm=SearchAlgorithm.PREFIX, limit=None)
    assert len(results) == 64
    assert {result.document.id for result in results} == set(range(64))
