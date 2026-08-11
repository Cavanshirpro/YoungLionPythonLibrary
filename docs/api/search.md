# Search API

YoungLion provides reusable primitives and ready-to-use layers.

`SearchIndex` + `InvertedIndex` retain corpus postings; `BM25Index` emphasizes full-text ranking. `FuzzyMatcher` exposes native Levenshtein, Damerau-Levenshtein, Jaro-Winkler, trigram and hybrid scores.

Specialized indexes: `AutocompleteIndex`, `MultiPatternSearch`, `NumericSearch`, `StructuredSearch`, `FileSearchEngine`, `ApplicationSearch`, `DDMSearchEngine`.

`SearchResult` carries score, document, algorithm, positions, matched terms and score details. Use `SearchQuery` when query settings should travel as a single value.
