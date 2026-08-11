# Search indexing performance

Indexes trade build time/memory for repeated-query speed. Exact DDM path indexes use reusable key buckets; `InvertedIndex` stores postings/document lengths for BM25; prefix/autocomplete uses sorted vocabulary caches.

Separate index-build time from query time when reporting benchmarks. Hybrid fuzzy search may limit candidate expansion for performance; pure prefix search keeps full prefix recall.
