# Search algorithm reference

YoungLion exposes several search techniques because no single algorithm is optimal for every query.

## Exact/hash lookup

Use for identifiers, names with exact semantics, status values and other equality-heavy DDM paths. After index construction, lookup avoids scanning every record.

## Sorted/range lookup

Use for numbers, timestamps and other ordered values. Lower/upper-bound style operations make ranges and nearest-neighbor-like queries cheaper than a full scan after construction.

## Inverted index + BM25

Use for document-style text where query words should rank documents by term importance and document length. BM25 is a ranking model, not typo correction.

## Prefix/autocomplete

Use for command palettes, names and input suggestions. Prefix indexes are optimized for leading-text queries; they are not replacements for contains/fuzzy search.

## Levenshtein

Counts insertions, deletions and substitutions. Useful as a general edit-distance measure. Cost grows with both string lengths.

## Damerau-Levenshtein

Adds adjacent transposition handling. This is often useful for human typing errors such as swapped characters.

## Jaro-Winkler

Useful for short names/identifiers and gives extra weight to a common prefix. It produces a similarity score rather than a raw edit count.

## Trigram / Dice similarity

Splits text into overlapping character trigrams and compares overlap. This can be a good candidate/ranking signal for longer strings.

## Hybrid search

Combines candidate generation and multiple scoring signals. Use when application-facing search should tolerate typos while still rewarding exact/prefix/token relevance.

## NumericSearch

Use for ordered numeric values, ranges and nearest values. It avoids converting numeric data into text-search problems.

## StructuredSearch

Use when records are mappings with explicit field predicates rather than free-text documents.

## Aho-Corasick multi-pattern search

Use when one text must be checked against many patterns at once—for example moderation keywords, signatures or local rule engines. It is generally better than independently scanning the full text once per pattern.

## DDM path indexes

Use `DDMSearchEngine` when the searchable unit is a structured DDM record and queries target paths like `profile.name` or `account.id`. The engine selects/reuses path-specific indexes instead of forcing application code to rebuild search logic.

## Choosing an algorithm

| Workload | First choice |
|---|---|
| exact nested field | DDM exact path index |
| numeric range | sorted DDM path index / `NumericSearch` |
| documents/articles | inverted index + BM25 |
| typo-tolerant short names | Damerau-Levenshtein / Jaro-Winkler / hybrid |
| command palette | autocomplete prefix index + fuzzy fallback |
| many patterns in one text | Aho-Corasick |
| mapping predicates | `StructuredSearch` |
| arbitrary one-off small list | simple scan/filter may be cheapest |
