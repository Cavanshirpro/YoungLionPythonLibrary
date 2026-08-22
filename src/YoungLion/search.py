"""YoungLion.search — ranked, fuzzy, autocomplete, structured and DDM-aware search.

This module provides a layered, dependency-free search toolkit.  Low-level native
similarity primitives feed reusable inverted/BM25 indexes; higher-level engines
cover autocomplete, multi-pattern matching, numeric ranges, structured records,
filesystem content and application search.  DDMSearchEngine adds reusable indexes
for dotted paths such as ``profile.name`` or ``economy.balance`` across ordinary
DDM-compatible iterables and YoungLion collection types.

The design separates one-time indexing cost from repeated query throughput.
Exact indexed lookups use hash structures; range operations use sorted index data;
ranked text search uses persistent posting lists/BM25; fuzzy matching is available
when exact terms are insufficient.  Mutating a source outside a collection-managed
path may require ``refresh()`` or ``invalidate()`` before querying again.

Compatibility classes GenerateTags, SearchData, Search and SearchFile remain
available for older call sites, while ApplicationSearch and DDMSearchEngine are
recommended for new application backends.
"""
from __future__ import annotations

import bisect
import itertools
import math
import re
from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Hashable, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

from . import _native

_WORD_RE = re.compile(r"[\w'-]+", re.UNICODE)


def _norm(text: Any, case_sensitive: bool = False) -> str:
    value = str(text)
    return value if case_sensitive else value.casefold()


def tokenize(text: Any, *, case_sensitive: bool = False, min_length: int = 1) -> List[str]:
    """Normalize text into the token sequence used by YoungLion search indexes.
    
    Parameters
    ----------
    text : Any
        Text/content input.
    case_sensitive : bool (default: ``False``)
        Whether string matching preserves case instead of using case-folded comparison.
    min_length : int (default: ``1``)
        Minimum token length retained by tokenization.
    
    Returns
    -------
    ``List[str]`` result described by the method semantics.
    """
    value = str(text) if case_sensitive else str(text).casefold()
    return [m.group(0) for m in _WORD_RE.finditer(value) if len(m.group(0)) >= min_length]


class SearchAlgorithm(str, Enum):
    """Search algorithm names.
    
    Overview
    --------
    ``SearchAlgorithm`` provides stable symbolic constants/enum-like values used to choose matching strategies.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use through SearchQuery/SearchIndex options rather than hard-coding implementation details.
    
    Inheritance
    -----------
    Base class(es): ``str, Enum``.
    """
    AUTO = "auto"
    HYBRID = "hybrid"
    EXACT = "exact"
    PREFIX = "prefix"
    SUBSTRING = "substring"
    REGEX = "regex"
    LEVENSHTEIN = "levenshtein"
    DAMERAU = "damerau"
    JARO_WINKLER = "jaro_winkler"
    TRIGRAM = "trigram"
    BM25 = "bm25"


@dataclass(slots=True)
class SearchDocument:
    """Indexed search document.
    
    Overview
    --------
    ``SearchDocument`` provides document identity, source value, normalized text/tokens, tags, metadata and searchable-text composition.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Used internally and available for inspection/custom integrations.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    searchable_text.
    """
    id: Hashable
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Tuple[str, ...] = ()
    fields: Dict[str, Any] = field(default_factory=dict)

    def searchable_text(self) -> str:
        """Return the document fields combined into the text used for indexing/search.
        
        Details
        -------
        This method belongs to :class:`SearchDocument` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        extras = [*self.tags]
        extras.extend(str(v) for v in self.fields.values() if v is not None)
        return " ".join([self.text, *extras]) if extras else self.text


@dataclass(slots=True, order=True)
class SearchResult:
    """Ranked search result.
    
    Overview
    --------
    ``SearchResult`` provides document reference, score and matching metadata with convenient source-value access.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Returned by result-oriented search APIs.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    value.
    """
    sort_index: float = field(init=False, repr=False)
    score: float
    document: SearchDocument = field(compare=False)
    algorithm: str = field(default="hybrid", compare=False)
    positions: Tuple[int, ...] = field(default=(), compare=False)
    matched_terms: Tuple[str, ...] = field(default=(), compare=False)
    details: Dict[str, float] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        self.score = float(self.score)
        self.sort_index = -self.score

    @property
    def value(self) -> Any:
        """Return the original application value associated with this search result.
        
        Details
        -------
        This method belongs to :class:`SearchResult` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        """
        return self.document.metadata.get("return", self.document)


@dataclass(slots=True)
class SearchStats:
    """Search index statistics.
    
    Overview
    --------
    ``SearchStats`` provides document/token/term counts describing an index snapshot.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Useful for diagnostics and monitoring.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
    documents: int
    tokens: int
    unique_tokens: int
    average_document_length: float


@dataclass(slots=True)
class SearchQuery:
    """Normalized search request.
    
    Overview
    --------
    ``SearchQuery`` provides query text plus algorithm, limits, scores, filters and regex flags.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Useful when constructing explicit repeatable search requests.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
    text: str
    algorithm: Union[SearchAlgorithm, str] = SearchAlgorithm.HYBRID
    limit: Optional[int] = 10
    min_score: float = 0.0
    filters: Optional[Mapping[str, Any]] = None
    regex_flags: int = 0


@dataclass(slots=True, frozen=True)
class Posting:
    """Inverted-index posting.
    
    Overview
    --------
    ``Posting`` provides document ID and term-frequency information.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Primarily useful for index inspection.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
    doc_id: Hashable
    term_frequency: int


@dataclass(slots=True)
class AutocompleteEntry:
    """Autocomplete candidate.
    
    Overview
    --------
    ``AutocompleteEntry`` provides display text, payload and ranking weight.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Stored by AutocompleteIndex.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
    term: str
    payload: Any = None
    weight: float = 1.0


@dataclass(slots=True, frozen=True)
class PatternMatch:
    """Multi-pattern match record.
    
    Overview
    --------
    ``PatternMatch`` provides matched pattern and text span metadata.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Returned by MultiPatternSearch.find.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
    pattern: str
    start: int
    end: int
    pattern_index: int


class FuzzyMatcher:
    """Native-accelerated fuzzy string matcher.
    
    Overview
    --------
    ``FuzzyMatcher`` provides Levenshtein, Damerau, Jaro-Winkler, trigram and hybrid similarity functions.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for typo-tolerant comparison; choose a metric appropriate to string length/error type.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    levenshtein, damerau_levenshtein, levenshtein_ratio, jaro_winkler, trigram, hybrid.
    """

    @staticmethod
    def levenshtein(a: str, b: str, *, case_sensitive: bool = False) -> int:
        """Return native Levenshtein edit distance between two strings.
        
        Details
        -------
        This method belongs to :class:`FuzzyMatcher` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return int(_native.levenshtein(_norm(a, case_sensitive), _norm(b, case_sensitive)))

    @staticmethod
    def damerau_levenshtein(a: str, b: str, *, case_sensitive: bool = False) -> int:
        """Return native Damerau-Levenshtein distance including adjacent transpositions.
        
        Details
        -------
        This method belongs to :class:`FuzzyMatcher` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return int(_native.damerau_levenshtein(_norm(a, case_sensitive), _norm(b, case_sensitive)))

    @staticmethod
    def levenshtein_ratio(a: str, b: str, *, damerau: bool = False, case_sensitive: bool = False) -> float:
        """Return a normalized 0..1 similarity ratio derived from edit distance.
        
        Details
        -------
        This method belongs to :class:`FuzzyMatcher` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        damerau : bool (default: ``False``)
            Whether the normalized edit ratio uses Damerau-Levenshtein distance.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        aa, bb = _norm(a, case_sensitive), _norm(b, case_sensitive)
        denom = max(len(aa), len(bb), 1)
        distance = _native.damerau_levenshtein(aa, bb) if damerau else _native.levenshtein(aa, bb)
        return max(0.0, 1.0 - float(distance) / denom)

    @staticmethod
    def jaro_winkler(a: str, b: str, *, case_sensitive: bool = False) -> float:
        """Return Jaro-Winkler similarity, useful for short names and prefix-preserving typos.
        
        Details
        -------
        This method belongs to :class:`FuzzyMatcher` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return float(_native.jaro_winkler(_norm(a, case_sensitive), _norm(b, case_sensitive)))

    @staticmethod
    def trigram(a: str, b: str, *, case_sensitive: bool = False) -> float:
        """Return trigram Dice-style similarity between two strings.
        
        Details
        -------
        This method belongs to :class:`FuzzyMatcher` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return float(_native.trigram_similarity(_norm(a, case_sensitive), _norm(b, case_sensitive)))

    @staticmethod
    def hybrid(a: str, b: str, *, case_sensitive: bool = False) -> float:
        """Combine multiple fuzzy signals into a general-purpose normalized similarity score.
        
        Details
        -------
        This method belongs to :class:`FuzzyMatcher` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        lev = FuzzyMatcher.levenshtein_ratio(a, b, damerau=True, case_sensitive=case_sensitive)
        jw = FuzzyMatcher.jaro_winkler(a, b, case_sensitive=case_sensitive)
        tri = FuzzyMatcher.trigram(a, b, case_sensitive=case_sensitive)
        return 0.35 * lev + 0.40 * jw + 0.25 * tri


class InvertedIndex:
    """Reusable token inverted index.
    
    Overview
    --------
    ``InvertedIndex`` provides posting lists, prefix/fuzzy term expansion, candidates and BM25 scoring.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Usually accessed through SearchIndex; exposed for advanced index inspection.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    add, remove, clear, tokens, postings, terms, prefix_terms, fuzzy_terms, candidate_ids, bm25, document_count, token_count, unique_token_count.
    """

    def __init__(self) -> None:
        """Initialize a new InvertedIndex instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self._postings: Dict[str, Dict[Hashable, int]] = {}
        self._tokens_by_doc: Dict[Hashable, Tuple[str, ...]] = {}
        self._lengths: Dict[Hashable, int] = {}
        self._total_tokens = 0
        self._sorted_terms: Optional[List[str]] = None

    def add(self, doc_id: Hashable, tokens: Iterable[str]) -> None:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        tokens : Iterable[str]
            Number of rate-limit tokens requested.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self.remove(doc_id)
        materialized = tuple(tokens)
        self._tokens_by_doc[doc_id] = materialized
        self._lengths[doc_id] = len(materialized)
        self._total_tokens += len(materialized)
        for term, frequency in Counter(materialized).items():
            self._postings.setdefault(term, {})[doc_id] = int(frequency)
        self._sorted_terms = None

    def remove(self, doc_id: Hashable) -> bool:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        old = self._tokens_by_doc.pop(doc_id, None)
        if old is None:
            return False
        self._total_tokens -= self._lengths.pop(doc_id, 0)
        for term in set(old):
            posting = self._postings.get(term)
            if posting is None:
                continue
            posting.pop(doc_id, None)
            if not posting:
                del self._postings[term]
        self._sorted_terms = None
        return True

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self._postings.clear()
        self._tokens_by_doc.clear()
        self._lengths.clear()
        self._total_tokens = 0
        self._sorted_terms = None

    def tokens(self, doc_id: Hashable) -> Tuple[str, ...]:
        """Perform the ``tokens`` operation for InvertedIndex.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        
        Returns
        -------
        ``Tuple[str, ...]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self._tokens_by_doc.get(doc_id, ())

    def postings(self, term: str) -> Tuple[Posting, ...]:
        """Perform the ``postings`` operation for InvertedIndex.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        term : str
            Value supplied for ``term`` according to the InvertedIndex contract.
        
        Returns
        -------
        ``Tuple[Posting, ...]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return tuple(Posting(doc_id, tf) for doc_id, tf in self._postings.get(term, {}).items())

    def terms(self) -> Iterator[str]:
        """Perform the ``terms`` operation for InvertedIndex.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Iterator[str]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return iter(self._postings)

    def prefix_terms(self, prefix: str, *, limit: Optional[int] = None) -> List[str]:
        """Return indexed terms beginning with a normalized prefix.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if not prefix:
            return []
        if self._sorted_terms is None:
            self._sorted_terms = sorted(self._postings)
        terms = self._sorted_terms
        start = bisect.bisect_left(terms, prefix)
        found: List[str] = []
        for index in range(start, len(terms)):
            term = terms[index]
            if not term.startswith(prefix):
                break
            found.append(term)
            if limit is not None and len(found) >= limit:
                break
        return found

    def fuzzy_terms(self, query: str, *, algorithm: Union[SearchAlgorithm, str] = SearchAlgorithm.HYBRID,
                    threshold: float = 0.60, limit: int = 8) -> List[Tuple[str, float]]:
        """Return similar indexed terms ranked by the selected fuzzy algorithm and threshold.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        threshold : float (default: ``0.6``)
            Value supplied for ``threshold`` according to the InvertedIndex contract.
        limit : int (default: ``8``)
            Maximum number of results/messages/suggestions to return.
        
        Returns
        -------
        ``List[Tuple[str, float]]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        algo = SearchAlgorithm(algorithm)
        scored: List[Tuple[float, str]] = []
        for term in self._postings:
            # Cheap length gate before invoking the native metric.
            if abs(len(term) - len(query)) > max(3, len(query) // 2):
                continue
            if algo is SearchAlgorithm.LEVENSHTEIN:
                score = FuzzyMatcher.levenshtein_ratio(query, term)
            elif algo is SearchAlgorithm.DAMERAU:
                score = FuzzyMatcher.levenshtein_ratio(query, term, damerau=True)
            elif algo is SearchAlgorithm.JARO_WINKLER:
                score = FuzzyMatcher.jaro_winkler(query, term)
            elif algo is SearchAlgorithm.TRIGRAM:
                score = FuzzyMatcher.trigram(query, term)
            else:
                score = FuzzyMatcher.hybrid(query, term)
            if score >= threshold:
                scored.append((score, term))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [(term, score) for score, term in scored[:max(0, int(limit))]]

    def candidate_ids(self, terms: Iterable[str]) -> set[Hashable]:
        """Return document IDs referenced by any of the supplied terms.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        terms : Iterable[str]
            Search/index terms.
        
        Returns
        -------
        ``set[Hashable]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ids: set[Hashable] = set()
        for term in terms:
            ids.update(self._postings.get(term, ()))
        return ids

    def bm25(self, query_tokens: Iterable[str], *, candidates: Optional[set[Hashable]] = None,
             k1: float = 1.5, b: float = 0.75) -> Dict[Hashable, float]:
        """Calculate BM25 relevance scores for query tokens over candidate documents.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query_tokens : Iterable[str]
            Value supplied for ``query_tokens`` according to the InvertedIndex contract.
        candidates : Optional[set[Hashable]] (default: ``None``)
            Value supplied for ``candidates`` according to the InvertedIndex contract.
        k1 : float (default: ``1.5``)
            BM25 term-frequency saturation parameter.
        b : float (default: ``0.75``)
            Second string/value.
        
        Returns
        -------
        ``Dict[Hashable, float]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        query = tuple(dict.fromkeys(query_tokens))
        if not query or not self._lengths:
            return {}
        n_docs = len(self._lengths)
        average = self._total_tokens / n_docs if n_docs else 0.0
        scores: Dict[Hashable, float] = {}
        for term in query:
            posting = self._postings.get(term)
            if not posting:
                continue
            df = len(posting)
            idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for doc_id, frequency in posting.items():
                if candidates is not None and doc_id not in candidates:
                    continue
                doc_len = self._lengths[doc_id]
                norm = 1.0 - b + b * (doc_len / average if average else 0.0)
                denominator = frequency + k1 * norm
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * (frequency * (k1 + 1.0)) / denominator
        return scores

    @property
    def document_count(self) -> int:
        """Return the number of documents currently represented by the index.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return len(self._lengths)

    @property
    def token_count(self) -> int:
        """Return the total number of indexed token occurrences.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self._total_tokens

    @property
    def unique_token_count(self) -> int:
        """Return the number of distinct indexed terms.
        
        Details
        -------
        This method belongs to :class:`InvertedIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return len(self._postings)


class SearchIndex:
    """General-purpose ranked in-memory index.
    
    Overview
    --------
    ``SearchIndex`` provides document lifecycle, filters and exact/contains/prefix/regex/fuzzy/BM25-oriented search.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for reusable text search where rebuilding per query would be wasteful.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    add, extend, remove, update, clear, stats, inverted_index, search.
    """

    def __init__(self, documents: Optional[Iterable[Union[SearchDocument, Mapping[str, Any], str]]] = None,
                 *, case_sensitive: bool = False):
        """Initialize a new SearchIndex instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        documents : Optional[Iterable[Union[SearchDocument, Mapping[str, Any], str]]] (default: ``None``)
            Iterable of initial/additional documents.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self.case_sensitive = bool(case_sensitive)
        self._docs: Dict[Hashable, SearchDocument] = {}
        self._texts: Dict[Hashable, str] = {}
        self._inverted = InvertedIndex()
        self._next_id = 0
        if documents:
            self.extend(documents)

    def _coerce(self, document: Union[SearchDocument, Mapping[str, Any], str], doc_id: Optional[Hashable] = None) -> SearchDocument:
        if isinstance(document, SearchDocument):
            return document
        if isinstance(document, str):
            if doc_id is None:
                self._next_id += 1
                doc_id = self._next_id
            return SearchDocument(doc_id, document)
        if isinstance(document, Mapping):
            identifier = document.get("id", doc_id)
            if identifier is None:
                self._next_id += 1
                identifier = self._next_id
            text = str(document.get("text", document.get("name", document.get("value", ""))))
            metadata = dict(document.get("metadata", {}))
            tags = tuple(str(x) for x in document.get("tags", ()))
            fields = dict(document.get("fields", {}))
            for key, value in document.items():
                if key not in {"id", "text", "name", "value", "metadata", "tags", "fields"}:
                    fields.setdefault(str(key), value)
            return SearchDocument(identifier, text, metadata, tags, fields)
        raise TypeError("document must be SearchDocument, mapping or str")

    def add(self, document: Union[SearchDocument, Mapping[str, Any], str], *, doc_id: Optional[Hashable] = None) -> SearchDocument:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        document : Union[SearchDocument, Mapping[str, Any], str]
            Document/value to add to the index.
        doc_id : Optional[Hashable] (default: ``None``)
            Stable document identifier.
        
        Returns
        -------
        ``SearchDocument`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        doc = self._coerce(document, doc_id)
        if doc.id in self._docs:
            self._inverted.remove(doc.id)
        searchable = doc.searchable_text()
        normalized = _norm(searchable, self.case_sensitive)
        tokens = tokenize(searchable, case_sensitive=self.case_sensitive)
        self._docs[doc.id] = doc
        self._texts[doc.id] = normalized
        self._inverted.add(doc.id, tokens)
        return doc

    def extend(self, documents: Iterable[Union[SearchDocument, Mapping[str, Any], str]]) -> "SearchIndex":
        """Add several documents to the index.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        documents : Iterable[Union[SearchDocument, Mapping[str, Any], str]]
            Iterable of initial/additional documents.
        
        Returns
        -------
        ``'SearchIndex'`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        for doc in documents:
            self.add(doc)
        return self

    def remove(self, doc_id: Hashable) -> bool:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if doc_id not in self._docs:
            return False
        del self._docs[doc_id]
        self._texts.pop(doc_id, None)
        self._inverted.remove(doc_id)
        return True

    def update(self, doc_id: Hashable, **changes: Any) -> SearchDocument:
        """Update top-level fields from mapping arguments and keyword values.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        **changes : Any
            Value supplied for ``changes`` according to the SearchIndex contract.
        
        Returns
        -------
        ``SearchDocument`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        old = self._docs[doc_id]
        doc = SearchDocument(
            doc_id,
            str(changes.get("text", old.text)),
            dict(changes.get("metadata", old.metadata)),
            tuple(changes.get("tags", old.tags)),
            dict(changes.get("fields", old.fields)),
        )
        return self.add(doc)

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self._docs.clear()
        self._texts.clear()
        self._inverted.clear()

    def __len__(self) -> int:
        return len(self._docs)

    def __iter__(self) -> Iterator[SearchDocument]:
        return iter(self._docs.values())

    def stats(self) -> SearchStats:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        count = self._inverted.token_count
        return SearchStats(
            len(self),
            count,
            self._inverted.unique_token_count,
            count / len(self) if self else 0.0,
        )

    @property
    def inverted_index(self) -> InvertedIndex:
        """Expose the reusable InvertedIndex backing this SearchIndex.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``InvertedIndex`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self._inverted

    @staticmethod
    def _passes_filters(doc: SearchDocument, filters: Optional[Mapping[str, Any]]) -> bool:
        if not filters:
            return True
        for key, expected in filters.items():
            actual = doc.fields.get(key, doc.metadata.get(key))
            if callable(expected):
                if not expected(actual):
                    return False
            elif isinstance(expected, (set, frozenset, tuple, list)) and not isinstance(expected, str):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True

    def _fuzzy_score(self, query: str, query_tokens: Sequence[str], tokens: Sequence[str], algorithm: SearchAlgorithm) -> float:
        if not tokens:
            return 0.0

        def best(part: str) -> float:
            if algorithm is SearchAlgorithm.LEVENSHTEIN:
                return max(FuzzyMatcher.levenshtein_ratio(part, token) for token in tokens)
            if algorithm is SearchAlgorithm.DAMERAU:
                return max(FuzzyMatcher.levenshtein_ratio(part, token, damerau=True) for token in tokens)
            if algorithm is SearchAlgorithm.JARO_WINKLER:
                return max(FuzzyMatcher.jaro_winkler(part, token) for token in tokens)
            if algorithm is SearchAlgorithm.TRIGRAM:
                return max(FuzzyMatcher.trigram(part, token) for token in tokens)
            return max(FuzzyMatcher.hybrid(part, token) for token in tokens)

        parts = query_tokens or (query,)
        return sum(best(part) for part in parts) / len(parts)

    def _candidate_ids(self, query_tokens: Sequence[str], algorithm: SearchAlgorithm) -> Optional[set[Hashable]]:
        # None means "all documents". Algorithms whose semantics inherently
        # inspect arbitrary text (regex/substring) cannot safely pre-filter.
        if algorithm in {SearchAlgorithm.SUBSTRING, SearchAlgorithm.REGEX, SearchAlgorithm.EXACT}:
            return None
        if algorithm is SearchAlgorithm.BM25:
            return self._inverted.candidate_ids(query_tokens)

        candidates = self._inverted.candidate_ids(query_tokens)
        for token in query_tokens:
            # Pure prefix search must preserve full recall. Hybrid/fuzzy search
            # intentionally caps vocabulary expansion to control worst-case work.
            prefix_limit = None if algorithm is SearchAlgorithm.PREFIX else 32
            prefix_terms = self._inverted.prefix_terms(token, limit=prefix_limit)
            candidates.update(self._inverted.candidate_ids(prefix_terms))
            if algorithm in {
                SearchAlgorithm.HYBRID,
                SearchAlgorithm.LEVENSHTEIN,
                SearchAlgorithm.DAMERAU,
                SearchAlgorithm.JARO_WINKLER,
                SearchAlgorithm.TRIGRAM,
            }:
                metric = algorithm if algorithm is not SearchAlgorithm.HYBRID else SearchAlgorithm.HYBRID
                fuzzy_terms = [term for term, _ in self._inverted.fuzzy_terms(token, algorithm=metric, threshold=0.52, limit=12)]
                candidates.update(self._inverted.candidate_ids(fuzzy_terms))
        # Fall back to the complete corpus for unusual queries where token-based
        # candidate generation found nothing; this preserves recall.
        return candidates or None

    def search(self, query: Union[str, SearchQuery], *, algorithm: Union[SearchAlgorithm, str] = SearchAlgorithm.HYBRID,
               limit: Optional[int] = 10, min_score: float = 0.0, filters: Optional[Mapping[str, Any]] = None,
               regex_flags: int = 0) -> List[SearchResult]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`SearchIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        limit : Optional[int] (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        min_score : float (default: ``0.0``)
            Minimum normalized/relevance score required for returned results.
        filters : Optional[Mapping[str, Any]] (default: ``None``)
            Optional field/metadata filters applied to candidate documents.
        regex_flags : int (default: ``0``)
            Flags passed to regular-expression matching.
        
        Returns
        -------
        ``List[SearchResult]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if isinstance(query, SearchQuery):
            spec = query
            query = spec.text
            algorithm = spec.algorithm
            limit = spec.limit
            min_score = spec.min_score
            filters = spec.filters
            regex_flags = spec.regex_flags
        elif not isinstance(query, str):
            query = str(query)

        if not query:
            return []
        algo = SearchAlgorithm(algorithm)
        if algo is SearchAlgorithm.AUTO:
            algo = SearchAlgorithm.HYBRID

        q = _norm(query, self.case_sensitive)
        qtokens = tokenize(query, case_sensitive=self.case_sensitive)
        candidate_ids = self._candidate_ids(qtokens, algo)
        if candidate_ids is None:
            docs = [doc for doc in self._docs.values() if self._passes_filters(doc, filters)]
        else:
            docs = [self._docs[doc_id] for doc_id in candidate_ids if doc_id in self._docs and self._passes_filters(self._docs[doc_id], filters)]
        if not docs:
            return []

        allowed_ids = {doc.id for doc in docs}
        bm25_map = self._inverted.bm25(qtokens, candidates=allowed_ids) if qtokens else {}
        bmmax = max(bm25_map.values(), default=0.0) or 1.0
        regex = None
        if algo is SearchAlgorithm.REGEX:
            flags = regex_flags if self.case_sensitive else regex_flags | re.IGNORECASE
            regex = re.compile(query, flags)

        results: List[SearchResult] = []
        for doc in docs:
            text = self._texts[doc.id]
            tokens = self._inverted.tokens(doc.id)
            positions: Tuple[int, ...] = ()
            details: Dict[str, float] = {}
            score = 0.0

            if algo is SearchAlgorithm.EXACT:
                score = 1.0 if text == q or q in tokens else 0.0
            elif algo is SearchAlgorithm.PREFIX:
                parts = qtokens or (q,)
                prefix_scores = [
                    max((1.0 if token == part else 0.85 for token in tokens if token.startswith(part)), default=0.0)
                    for part in parts
                ]
                score = sum(prefix_scores) / len(prefix_scores)
            elif algo is SearchAlgorithm.SUBSTRING:
                positions = tuple(_native.find_all(text, q))
                score = min(1.0, 0.75 + 0.05 * len(positions)) if positions else 0.0
            elif algo is SearchAlgorithm.REGEX:
                raw = doc.searchable_text()
                matches = list(regex.finditer(raw)) if regex else []
                positions = tuple(match.start() for match in matches)
                score = min(1.0, 0.70 + 0.05 * len(matches)) if matches else 0.0
            elif algo is SearchAlgorithm.BM25:
                score = bm25_map.get(doc.id, 0.0)
            elif algo in {
                SearchAlgorithm.LEVENSHTEIN,
                SearchAlgorithm.DAMERAU,
                SearchAlgorithm.JARO_WINKLER,
                SearchAlgorithm.TRIGRAM,
            }:
                score = self._fuzzy_score(q, qtokens, tokens, algo)
            else:
                exact_phrase = 1.0 if q == text else (0.92 if q in text else 0.0)
                positions = tuple(_native.find_all(text, q)) if q in text else ()
                parts = qtokens or (q,)
                prefix_scores = [
                    max((1.0 if token == part else 0.85 for token in tokens if token.startswith(part)), default=0.0)
                    for part in parts
                ]
                prefix = sum(prefix_scores) / len(prefix_scores)
                fuzzy = self._fuzzy_score(q, qtokens, tokens, SearchAlgorithm.HYBRID)
                bm = bm25_map.get(doc.id, 0.0) / bmmax
                score = min(1.0, 0.42 * bm + 0.28 * exact_phrase + 0.15 * prefix + 0.15 * fuzzy)
                details = {"bm25": bm, "phrase": exact_phrase, "prefix": prefix, "fuzzy": fuzzy}

            if score >= min_score and score > 0:
                matched = tuple(token for token in qtokens if token in tokens)
                results.append(SearchResult(score, doc, algo.value, positions, matched, details))

        results.sort()
        return results if limit is None else results[:max(0, int(limit))]


class BM25Index(SearchIndex):
    """BM25-focused SearchIndex.
    
    Overview
    --------
    ``BM25Index`` provides SearchIndex behavior with BM25 as the natural ranked retrieval path.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for document relevance ranking over repeated queries.
    
    Inheritance
    -----------
    Base class(es): ``SearchIndex``.
    
    Primary public operations
    -------------------------
    search.
    """
    def search(self, query: Union[str, SearchQuery], **kwargs: Any) -> List[SearchResult]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`BM25Index` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[SearchResult]`` result described by the method semantics.
        """
        if isinstance(query, SearchQuery):
            query = SearchQuery(query.text, SearchAlgorithm.BM25, query.limit, query.min_score, query.filters, query.regex_flags)
            return super().search(query)
        kwargs["algorithm"] = SearchAlgorithm.BM25
        return super().search(query, **kwargs)


class AutocompleteIndex:
    """Weighted autocomplete index.
    
    Overview
    --------
    ``AutocompleteIndex`` provides prefix suggestions with optional fuzzy fallback and payloads.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for command palettes, search boxes and route/entity completion.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    add, suggest.
    """

    def __init__(self, entries: Iterable[Union[str, AutocompleteEntry, Tuple[str, Any], Tuple[str, Any, float]]] = (),
                 *, case_sensitive: bool = False):
        """Initialize a new AutocompleteIndex instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`AutocompleteIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        entries : Iterable[Union[str, AutocompleteEntry, Tuple[str, Any], Tuple[str, Any, float]]] (default: ``()``)
            Initial autocomplete/index entries.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        self.case_sensitive = bool(case_sensitive)
        self._entries: List[AutocompleteEntry] = []
        self._keys: List[str] = []
        self._dirty = False
        for entry in entries:
            self.add(entry)

    def add(self, entry: Union[str, AutocompleteEntry, Tuple[str, Any], Tuple[str, Any, float]], payload: Any = None,
            weight: float = 1.0) -> AutocompleteEntry:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`AutocompleteIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        entry : Union[str, AutocompleteEntry, Tuple[str, Any], Tuple[str, Any, float]]
            Structured or textual log entry to persist.
        payload : Any (default: ``None``)
            Application value associated with an indexed entry/document.
        weight : float (default: ``1.0``)
            Ranking weight applied to an autocomplete entry.
        
        Returns
        -------
        ``AutocompleteEntry`` result described by the method semantics.
        """
        if isinstance(entry, AutocompleteEntry):
            obj = entry
        elif isinstance(entry, str):
            obj = AutocompleteEntry(entry, payload, float(weight))
        else:
            values = tuple(entry)
            if len(values) == 2:
                obj = AutocompleteEntry(str(values[0]), values[1], 1.0)
            elif len(values) == 3:
                obj = AutocompleteEntry(str(values[0]), values[1], float(values[2]))
            else:
                raise ValueError("autocomplete tuple must contain (term, payload) or (term, payload, weight)")
        self._entries.append(obj)
        self._dirty = True
        return obj

    def _rebuild(self) -> None:
        if not self._dirty:
            return
        self._entries.sort(key=lambda item: (_norm(item.term, self.case_sensitive), -item.weight, item.term))
        self._keys = [_norm(item.term, self.case_sensitive) for item in self._entries]
        self._dirty = False

    def suggest(self, prefix: str, *, limit: int = 10, fuzzy_fallback: bool = True, min_score: float = 0.62) -> List[AutocompleteEntry]:
        """Return ranked autocomplete candidates for a prefix with optional fuzzy fallback.
        
        Details
        -------
        This method belongs to :class:`AutocompleteIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : int (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        fuzzy_fallback : bool (default: ``True``)
            Whether autocomplete may fall back to fuzzy matching when prefix matches are insufficient.
        min_score : float (default: ``0.62``)
            Minimum normalized/relevance score required for returned results.
        
        Returns
        -------
        ``List[AutocompleteEntry]`` result described by the method semantics.
        """
        self._rebuild()
        key = _norm(prefix, self.case_sensitive)
        if not key:
            ranked = sorted(self._entries, key=lambda item: (-item.weight, item.term))
            return ranked[:max(0, int(limit))]
        lo = bisect.bisect_left(self._keys, key)
        hi = bisect.bisect_left(self._keys, key + chr(0x10FFFF))
        direct = [entry for entry, normalized in zip(self._entries[lo:hi], self._keys[lo:hi]) if normalized.startswith(key)]
        direct.sort(key=lambda item: (-item.weight, len(item.term), item.term))
        if direct or not fuzzy_fallback:
            return direct[:max(0, int(limit))]
        scored = []
        for entry, normalized in zip(self._entries, self._keys):
            score = FuzzyMatcher.hybrid(key, normalized, case_sensitive=True)
            if score >= min_score:
                scored.append((score * max(0.0, entry.weight), entry))
        scored.sort(key=lambda item: (-item[0], len(item[1].term), item[1].term))
        return [entry for _, entry in scored[:max(0, int(limit))]]

    def __len__(self) -> int:
        return len(self._entries)


class MultiPatternSearch:
    """Aho-Corasick style multi-pattern matcher.
    
    Overview
    --------
    ``MultiPatternSearch`` provides one-pass discovery of many literal patterns in text.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for moderation keywords, signatures and dictionary matching.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    find, contains_any.
    """

    def __init__(self, patterns: Iterable[str], *, case_sensitive: bool = False):
        """Initialize a new MultiPatternSearch instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`MultiPatternSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        patterns : Iterable[str]
            Patterns indexed by MultiPatternSearch.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        self.case_sensitive = bool(case_sensitive)
        self.patterns = tuple(str(pattern) for pattern in patterns)
        self._normalized = tuple(_norm(pattern, self.case_sensitive) for pattern in self.patterns)
        self._goto: List[Dict[str, int]] = [{}]
        self._fail: List[int] = [0]
        self._out: List[List[int]] = [[]]
        self._build()

    def _new_state(self) -> int:
        self._goto.append({})
        self._fail.append(0)
        self._out.append([])
        return len(self._goto) - 1

    def _build(self) -> None:
        for pattern_index, pattern in enumerate(self._normalized):
            if not pattern:
                continue
            state = 0
            for char in pattern:
                next_state = self._goto[state].get(char)
                if next_state is None:
                    next_state = self._new_state()
                    self._goto[state][char] = next_state
                state = next_state
            self._out[state].append(pattern_index)

        queue: deque[int] = deque()
        for state in self._goto[0].values():
            queue.append(state)
        while queue:
            state = queue.popleft()
            for char, child in self._goto[state].items():
                queue.append(child)
                fallback = self._fail[state]
                while fallback and char not in self._goto[fallback]:
                    fallback = self._fail[fallback]
                self._fail[child] = self._goto[fallback].get(char, 0)
                self._out[child].extend(self._out[self._fail[child]])

    def find(self, text: str) -> List[PatternMatch]:
        """Return tree/search records that satisfy a predicate or query.
        
        Details
        -------
        This method belongs to :class:`MultiPatternSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : str
            Text/content input.
        
        Returns
        -------
        ``List[PatternMatch]`` result described by the method semantics.
        """
        normalized = _norm(text, self.case_sensitive)
        state = 0
        matches: List[PatternMatch] = []
        for index, char in enumerate(normalized):
            while state and char not in self._goto[state]:
                state = self._fail[state]
            state = self._goto[state].get(char, 0)
            for pattern_index in self._out[state]:
                pattern = self._normalized[pattern_index]
                start = index - len(pattern) + 1
                matches.append(PatternMatch(self.patterns[pattern_index], start, index + 1, pattern_index))
        return matches

    def contains_any(self, text: str) -> bool:
        """Return whether any configured pattern occurs in the supplied text.
        
        Details
        -------
        This method belongs to :class:`MultiPatternSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : str
            Text/content input.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        normalized = _norm(text, self.case_sensitive)
        state = 0
        for char in normalized:
            while state and char not in self._goto[state]:
                state = self._fail[state]
            state = self._goto[state].get(char, 0)
            if self._out[state]:
                return True
        return False


class NumericSearch:
    """Sorted numeric search index.
    
    Overview
    --------
    ``NumericSearch`` provides range lookup and nearest-neighbor queries over numeric values with payloads.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for prices, scores, measurements and other one-dimensional numeric fields.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    add, range, nearest.
    """

    def __init__(self, values: Iterable[Tuple[float, Any]] = ()):
        """Initialize a new NumericSearch instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`NumericSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        values : Iterable[Tuple[float, Any]] (default: ``()``)
            Input iterable, mapping values or composite lookup values.
        """
        items = sorted(((float(value), index, payload) for index, (value, payload) in enumerate(values)), key=lambda item: (item[0], item[1]))
        self._values: List[float] = [item[0] for item in items]
        self._payloads: List[Any] = [item[2] for item in items]

    def add(self, value: float, payload: Any = None) -> None:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`NumericSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : float
            Target, new or comparison value.
        payload : Any (default: ``None``)
            Application value associated with an indexed entry/document.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        numeric = float(value)
        position = bisect.bisect_right(self._values, numeric)
        self._values.insert(position, numeric)
        self._payloads.insert(position, payload)

    def range(self, minimum: float, maximum: float) -> List[Tuple[float, Any]]:
        """Return indexed entries inside numeric/string bounds according to inclusion flags.
        
        Details
        -------
        This method belongs to :class:`NumericSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        minimum : float
            Lower bound or minimum accepted value.
        maximum : float
            Upper bound or maximum accepted value.
        
        Returns
        -------
        ``List[Tuple[float, Any]]`` result described by the method semantics.
        """
        lo = bisect.bisect_left(self._values, float(minimum))
        hi = bisect.bisect_right(self._values, float(maximum))
        return list(zip(self._values[lo:hi], self._payloads[lo:hi]))

    def nearest(self, value: float, k: int = 1) -> List[Tuple[float, Any]]:
        """Return the k numerically nearest indexed entries to a target value.
        
        Details
        -------
        This method belongs to :class:`NumericSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : float
            Target, new or comparison value.
        k : int (default: ``1``)
            Value supplied for ``k`` according to the NumericSearch contract.
        
        Returns
        -------
        ``List[Tuple[float, Any]]`` result described by the method semantics.
        """
        if k <= 0:
            return []
        target = float(value)
        position = bisect.bisect_left(self._values, target)
        left, right = position - 1, position
        out: List[Tuple[float, Any]] = []
        while len(out) < k and (left >= 0 or right < len(self._values)):
            if left < 0:
                out.append((self._values[right], self._payloads[right])); right += 1
            elif right >= len(self._values):
                out.append((self._values[left], self._payloads[left])); left -= 1
            elif abs(self._values[left] - target) <= abs(self._values[right] - target):
                out.append((self._values[left], self._payloads[left])); left -= 1
            else:
                out.append((self._values[right], self._payloads[right])); right += 1
        return out

    def __len__(self) -> int:
        return len(self._values)


class StructuredSearch:
    """Field-weighted record search.
    
    Overview
    --------
    ``StructuredSearch`` provides indexing mapping-like records with configurable field weights.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when free-text relevance must span several known structured fields.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    add, search.
    """

    def __init__(self, records: Iterable[Mapping[str, Any]] = (), *, id_field: str = "id",
                 field_weights: Optional[Mapping[str, float]] = None, case_sensitive: bool = False):
        """Initialize a new StructuredSearch instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`StructuredSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        records : Iterable[Mapping[str, Any]] (default: ``()``)
            Input records for structured/DDM collection indexing.
        id_field : str (default: ``'id'``)
            Record field used to derive stable document identifiers.
        field_weights : Optional[Mapping[str, float]] (default: ``None``)
            Per-field search ranking weights.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        self.id_field = id_field
        self.field_weights = dict(field_weights or {})
        self.index = SearchIndex(case_sensitive=case_sensitive)
        for record in records:
            self.add(record)

    def add(self, record: Mapping[str, Any]) -> SearchDocument:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`StructuredSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        record : Mapping[str, Any]
            Value supplied for ``record`` according to the StructuredSearch contract.
        
        Returns
        -------
        ``SearchDocument`` result described by the method semantics.
        """
        data = dict(record)
        record_id = data.get(self.id_field, len(self.index) + 1)
        pieces: List[str] = []
        for key, value in data.items():
            if key == self.id_field or value is None:
                continue
            weight = max(1, int(round(self.field_weights.get(key, 1.0) * 2)))
            pieces.extend([str(value)] * weight)
        return self.index.add(SearchDocument(record_id, " ".join(pieces), metadata={"record": data}, fields=data))

    def search(self, query: Union[str, SearchQuery], **kwargs: Any) -> List[SearchResult]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`StructuredSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[SearchResult]`` result described by the method semantics.
        """
        return self.index.search(query, **kwargs)


class FileSearchEngine:
    """Filesystem search backend.
    
    Overview
    --------
    ``FileSearchEngine`` provides path/name metadata indexing with optional bounded file-content indexing.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for local application file search; call refresh after external filesystem changes.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    refresh, search_results, search.
    """

    def __init__(self, root: Union[str, Path] = ".", *, content: bool = False, max_content_bytes: int = 2_000_000,
                 extensions: Optional[Iterable[str]] = None, case_sensitive: bool = False):
        """Initialize a new FileSearchEngine instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`FileSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        root : Union[str, Path] (default: ``'.'``)
            Root directory for filesystem search.
        content : bool (default: ``False``)
            Text/bytes/content payload to write, search or convert.
        max_content_bytes : int (default: ``2000000``)
            Value supplied for ``max_content_bytes`` according to the FileSearchEngine contract.
        extensions : Optional[Iterable[str]] (default: ``None``)
            Allowed file extensions, typically including leading dots.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        self.root = Path(root)
        self.content = bool(content)
        self.max_content_bytes = int(max_content_bytes)
        self.extensions = {
            value.lower() if str(value).startswith(".") else "." + str(value).lower()
            for value in extensions
        } if extensions else None
        self.index = SearchIndex(case_sensitive=case_sensitive)
        self.refresh()

    def refresh(self) -> "FileSearchEngine":
        """Rebuild class-specific cached/indexed state from the current source.
        
        Details
        -------
        This method belongs to :class:`FileSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'FileSearchEngine'`` result described by the method semantics.
        """
        self.index.clear()
        if not self.root.exists():
            return self
        for path in self.root.rglob("*"):
            try:
                if not path.is_file():
                    continue
                if self.extensions and path.suffix.lower() not in self.extensions:
                    continue
                stat = path.stat()
                text = f"{path.name} {path.as_posix()}"
                if self.content and stat.st_size <= self.max_content_bytes:
                    try:
                        text += " " + path.read_text(encoding="utf-8", errors="ignore")
                    except OSError:
                        pass
                self.index.add(SearchDocument(
                    str(path),
                    text,
                    metadata={"path": str(path), "return": str(path)},
                    fields={"name": path.name, "extension": path.suffix.lower(), "size": stat.st_size, "mtime": stat.st_mtime},
                ))
            except OSError:
                continue
        return self

    def search_results(self, query: Union[str, SearchQuery], *, extension: Optional[Union[str, Sequence[str]]] = None,
                       min_size: Optional[int] = None, max_size: Optional[int] = None, **kwargs: Any) -> List[SearchResult]:
        """Return rich SearchResult-style objects rather than only application payloads/values.
        
        Details
        -------
        This method belongs to :class:`FileSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        extension : Optional[Union[str, Sequence[str]]] (default: ``None``)
            Value supplied for ``extension`` according to the FileSearchEngine contract.
        min_size : Optional[int] (default: ``None``)
            Optional minimum file/content size filter.
        max_size : Optional[int] (default: ``None``)
            Maximum number of cache entries retained.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[SearchResult]`` result described by the method semantics.
        """
        filters: Dict[str, Any] = dict(kwargs.pop("filters", {}) or {})
        if extension is not None:
            extensions = [extension] if isinstance(extension, str) else extension
            filters["extension"] = {
                value.lower() if value.startswith(".") else "." + value.lower()
                for value in extensions
            }
        if min_size is not None or max_size is not None:
            filters["size"] = lambda size: size is not None and (min_size is None or size >= min_size) and (max_size is None or size <= max_size)
        if isinstance(query, SearchQuery):
            merged_filters = dict(query.filters or {})
            merged_filters.update(filters)
            query = SearchQuery(query.text, query.algorithm, query.limit, query.min_score, merged_filters, query.regex_flags)
            return self.index.search(query, **kwargs)
        return self.index.search(query, filters=filters, **kwargs)

    def search(self, query: Union[str, SearchQuery], **kwargs: Any) -> List[str]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`FileSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return [result.document.metadata["path"] for result in self.search_results(query, **kwargs)]


class GenerateTags:
    """Legacy tag generator.
    
    Overview
    --------
    ``GenerateTags`` provides normalization, replacement, stop-word filtering and n-gram style tag generation.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Retained for compatibility; new full-text systems should prefer SearchIndex/ApplicationSearch.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    get_tags.
    """

    def __init__(self, terms: Union[str, List[str]], lowercase: bool = True, clean_special_chars: bool = True,
                 min_words: int = 1, max_words: Optional[int] = None, replacements: Optional[dict] = None,
                 stop_words: Optional[List[str]] = None, max_tags: int = 10_000):
        """Initialize a new GenerateTags instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`GenerateTags` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        terms : Union[str, List[str]]
            Search/index terms.
        lowercase : bool (default: ``True``)
            Value supplied for ``lowercase`` according to the GenerateTags contract.
        clean_special_chars : bool (default: ``True``)
            Value supplied for ``clean_special_chars`` according to the GenerateTags contract.
        min_words : int (default: ``1``)
            Minimum words per generated tag.
        max_words : Optional[int] (default: ``None``)
            Maximum words per generated tag.
        replacements : Optional[dict] (default: ``None``)
            Text replacement mapping used while generating tags.
        stop_words : Optional[List[str]] (default: ``None``)
            Words excluded from generated tags.
        max_tags : int (default: ``10000``)
            Maximum generated tags retained.
        """
        self.terms = terms.split() if isinstance(terms, str) else list(terms) if isinstance(terms, list) else None
        if self.terms is None:
            raise ValueError("Terms must be either a string or a list of words.")
        self.lowercase = lowercase
        self.clean_special_chars = clean_special_chars
        self.min_words = max(1, int(min_words))
        self.replacements = replacements or {}
        self.stop_words = {_norm(value) for value in (stop_words or [])}
        self.max_tags = max(1, int(max_tags))
        self.terms = self._preprocess_terms(self.terms)
        self.max_words = min(max_words or len(self.terms), len(self.terms))

    def _preprocess_terms(self, terms: Iterable[str]) -> List[str]:
        out: List[str] = []
        for term in terms:
            value = str(term)
            if self.clean_special_chars:
                value = re.sub(r"[^\w ]", "", value, flags=re.UNICODE)
            if self.lowercase:
                value = value.casefold()
            if value and _norm(value) not in self.stop_words:
                out.append(value)
        return out

    def get_tags(self) -> List[str]:
        """Return normalized/generated tags for the legacy compatibility object.
        
        Details
        -------
        This method belongs to :class:`GenerateTags` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        tags: set[str] = set()
        variants = [[term, str(self.replacements[term])] if term in self.replacements else [term] for term in self.terms]
        for variant in itertools.product(*variants):
            for size in range(self.min_words, self.max_words + 1):
                for combo in itertools.combinations(variant, size):
                    for permutation in itertools.permutations(combo):
                        tags.add(" ".join(permutation))
                        if len(tags) >= self.max_tags:
                            return sorted(tags)
        return sorted(tags)


class SearchData:
    """Legacy tag-to-data adapter.
    
    Overview
    --------
    ``SearchData`` provides tag generation and retrieval over a collection of values.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Retained for compatibility.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    get_tags, get.
    """

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize a new SearchData instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`SearchData` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : List[Dict[str, Any]]
            Input mapping or record data used to initialize the object.
        """
        self._structured_data: Dict[str, List[Any]] = {}
        self._index = SearchIndex()
        for entry in data:
            tags = [str(tag) for tag in entry.get("tags", [])]
            value = entry.get("return")
            if not tags or value is None:
                continue
            for tag in tags:
                self._structured_data.setdefault(tag, []).append(value)
            self._index.add(SearchDocument(len(self._index) + 1, " ".join(tags), metadata={"return": value}, tags=tuple(tags)))

    def get_tags(self) -> List[str]:
        """Return normalized/generated tags for the legacy compatibility object.
        
        Details
        -------
        This method belongs to :class:`SearchData` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return list(self._structured_data)

    def get(self, tag: str) -> List[Any]:
        """Return a value for a key, falling back to a default when the key is absent.
        
        Details
        -------
        This method belongs to :class:`SearchData` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        tag : str
            Value supplied for ``tag`` according to the SearchData contract.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        """
        return list(self._structured_data.get(tag, ()))

    def __getitem__(self, tag: str) -> List[Any]:
        return self.get(tag)

    def __contains__(self, tag: str) -> bool:
        return tag in self._structured_data

    def __repr__(self) -> str:
        return repr(self._structured_data)


class Search:
    """Legacy compatibility search facade.
    
    Overview
    --------
    ``Search`` provides simple query and ranked query methods over SearchData.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use ApplicationSearch/SearchIndex for new systems.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    search, ranked.
    """

    def __init__(self, sdata: SearchData, only_tag: bool = False):
        """Initialize a new Search instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Search` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        sdata : SearchData
            SearchData instance used by the compatibility Search facade.
        only_tag : bool (default: ``False``)
            Restrict compatibility search behavior to tags where supported.
        """
        self.sdata = sdata
        self.only_tag = only_tag

    def search(self, query: str) -> List[Any]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`Search` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        """
        if self.only_tag:
            return self.sdata.get(query)
        results = self.sdata._index.search(query, algorithm=SearchAlgorithm.HYBRID, limit=5, min_score=0.18)
        out: List[Any] = []
        for result in results:
            value = result.document.metadata.get("return")
            if value not in out:
                out.append(value)
        return out

    def ranked(self, query: str, **kwargs: Any) -> List[SearchResult]:
        """Run the legacy facade through the ranked search engine and return scored results.
        
        Details
        -------
        This method belongs to :class:`Search` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[SearchResult]`` result described by the method semantics.
        """
        return self.sdata._index.search(query, **kwargs)


class SearchFile(FileSearchEngine):
    """Legacy filesystem search facade.
    
    Overview
    --------
    ``SearchFile`` provides simple name/content search rooted at a directory.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use FileSearchEngine for richer result metadata and indexing.
    
    Inheritance
    -----------
    Base class(es): ``FileSearchEngine``.
    
    Primary public operations
    -------------------------
    search.
    """

    def __init__(self, root: Union[str, Path] = "."):
        """Initialize a new SearchFile instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`SearchFile` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        root : Union[str, Path] (default: ``'.'``)
            Root directory for filesystem search.
        """
        super().__init__(root, content=False)

    def search(self, query: str, content: bool = False, case_sensitive: bool = False) -> List[str]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`SearchFile` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        content : bool (default: ``False``)
            Text/bytes/content payload to write, search or convert.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        if content != self.content or case_sensitive != self.index.case_sensitive:
            self.content = content
            self.index.case_sensitive = case_sensitive
            self.refresh()
        return super().search(query, algorithm=SearchAlgorithm.HYBRID, limit=10_000, min_score=0.12)


__all__ = [
    "SearchAlgorithm",
    "SearchDocument",
    "SearchResult",
    "SearchStats",
    "SearchQuery",
    "Posting",
    "AutocompleteEntry",
    "PatternMatch",
    "FuzzyMatcher",
    "InvertedIndex",
    "SearchIndex",
    "BM25Index",
    "AutocompleteIndex",
    "MultiPatternSearch",
    "NumericSearch",
    "StructuredSearch",
    "FileSearchEngine",
    "GenerateTags",
    "SearchData",
    "Search",
    "SearchFile",
    "tokenize",
]

# ---------------------------------------------------------------------------
# Application and DDM-aware search infrastructure
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class DDMSearchHit:
    """DDM text-search hit.
    
    Overview
    --------
    ``DDMSearchHit`` provides source key/object, path value and score metadata.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Returned when DDMSearchEngine.text is requested with hit metadata.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
    item: Any
    key: Any
    path: str
    value: Any
    score: float = 1.0
    algorithm: str = "exact"


def _index_key(value: Any) -> Any:
    """Convert common mutable values to stable exact-index keys."""
    try:
        hash(value)
        return value
    except TypeError:
        if isinstance(value, Mapping):
            return tuple(sorted((str(k), _index_key(v)) for k, v in value.items()))
        if isinstance(value, (list, tuple)):
            return tuple(_index_key(v) for v in value)
        if isinstance(value, (set, frozenset)):
            return frozenset(_index_key(v) for v in value)
        return repr(value)


class DDMPathIndex:
    """Single dotted-path DDM index.
    
    Overview
    --------
    ``DDMPathIndex`` provides exact hash lookup, sorted ranges, prefix/contains and optional text index.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Built by DDMSearchEngine and reusable across many queries.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    exact, range, prefix, text, contains, stats.
    """

    __slots__ = (
        "path", "case_sensitive", "_entries", "_exact", "_numbers", "_strings",
        "_number_keys", "_string_keys", "_text", "_values", "_objects",
    )

    def __init__(self, path: str, entries: Sequence[Tuple[Any, Any]], *, text: bool = True,
                 case_sensitive: bool = False, objects: Optional[Mapping[Any, Any]] = None):
        """Initialize a new DDMPathIndex instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        entries : Sequence[Tuple[Any, Any]]
            Initial autocomplete/index entries.
        text : bool (default: ``True``)
            Text/content input.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        objects : Optional[Mapping[Any, Any]] (default: ``None``)
            Optional shared key-to-object mapping reused by DDM indexes.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self.path = str(path)
        self.case_sensitive = bool(case_sensitive)
        self._entries = entries if isinstance(entries, list) else list(entries)
        self._exact: Dict[Any, List[Any]] = {}
        self._numbers: List[Tuple[float, int, Any]] = []
        self._strings: List[Tuple[str, int, Any]] = []
        self._number_keys: List[Tuple[float, int]] = []
        self._string_keys: List[Tuple[str, int]] = []
        self._text = SearchIndex(case_sensitive=case_sensitive) if text else None
        self._values: Dict[Any, Any] = {}
        self._objects: Mapping[Any, Any] = dict(self._entries) if objects is None else objects
        self._build()
        # Entries are only needed while constructing the path-specific structures.
        # Drop the duplicate list afterwards; the shared object store resolves keys.
        self._entries = ()

    def _build(self) -> None:
        missing = object()
        for ordinal, (key, item) in enumerate(self._entries):
            value = _native.ddm_get_path(item, self.path, missing)
            if value is missing:
                continue
            self._values[key] = value
            self._exact.setdefault(_index_key(value), []).append(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                self._numbers.append((float(value), ordinal, key))
            elif isinstance(value, str):
                normalized = _norm(value, self.case_sensitive)
                self._strings.append((normalized, ordinal, key))
                if self._text is not None:
                    self._text.add(SearchDocument(key, value, metadata={"source_key": key}, fields={"path": self.path}))
        self._numbers.sort(key=lambda x: (x[0], x[1]))
        self._strings.sort(key=lambda x: (x[0], x[1]))
        self._number_keys = [(row[0], row[1]) for row in self._numbers]
        self._string_keys = [(row[0], row[1]) for row in self._strings]

    def exact(self, value: Any) -> List[DDMSearchHit]:
        """Return records whose indexed dotted-path value exactly equals the target.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``List[DDMSearchHit]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return [DDMSearchHit(self._objects[key], key, self.path, self._values[key]) for key in self._exact.get(_index_key(value), ())]

    def range(self, minimum: Any = None, maximum: Any = None, *, include_min: bool = True,
              include_max: bool = True) -> List[DDMSearchHit]:
        """Return indexed entries inside numeric/string bounds according to inclusion flags.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        minimum : Any (default: ``None``)
            Lower bound or minimum accepted value.
        maximum : Any (default: ``None``)
            Upper bound or maximum accepted value.
        include_min : bool (default: ``True``)
            Whether a lower range bound is inclusive.
        include_max : bool (default: ``True``)
            Whether an upper range bound is inclusive.
        
        Returns
        -------
        ``List[DDMSearchHit]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if isinstance(minimum, str) or isinstance(maximum, str):
            rows = self._strings
            lo_value = "" if minimum is None else _norm(minimum, self.case_sensitive)
            hi_value = chr(0x10FFFF) * 4 if maximum is None else _norm(maximum, self.case_sensitive)
        else:
            rows = self._numbers
            lo_value = -math.inf if minimum is None else float(minimum)
            hi_value = math.inf if maximum is None else float(maximum)
        keys_only = self._string_keys if rows is self._strings else self._number_keys
        if include_min:
            lo = bisect.bisect_left(keys_only, (lo_value, -1))
        else:
            lo = bisect.bisect_right(keys_only, (lo_value, 10**30))
        if include_max:
            hi = bisect.bisect_right(keys_only, (hi_value, 10**30))
        else:
            hi = bisect.bisect_left(keys_only, (hi_value, -1))
        return [DDMSearchHit(self._objects[key], key, self.path, self._values[key], 1.0, "range") for _, _, key in rows[lo:hi]]

    def prefix(self, prefix: str, *, limit: Optional[int] = None) -> List[DDMSearchHit]:
        """Return records whose indexed string value begins with the supplied prefix.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.
        
        Returns
        -------
        ``List[DDMSearchHit]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        q = _norm(prefix, self.case_sensitive)
        lo = bisect.bisect_left(self._string_keys, (q, -1))
        out: List[DDMSearchHit] = []
        for value, _, key in self._strings[lo:]:
            if not value.startswith(q):
                break
            out.append(DDMSearchHit(self._objects[key], key, self.path, self._values[key], 1.0, "prefix"))
            if limit is not None and len(out) >= limit:
                break
        return out

    def text(self, query: str, *, algorithm: Union[SearchAlgorithm, str] = SearchAlgorithm.HYBRID,
             limit: Optional[int] = 10, min_score: float = 0.0) -> List[DDMSearchHit]:
        """Perform the ``text`` operation for DDMPathIndex.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        limit : Optional[int] (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        min_score : float (default: ``0.0``)
            Minimum normalized/relevance score required for returned results.
        
        Returns
        -------
        ``List[DDMSearchHit]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if self._text is None:
            return []
        return [
            DDMSearchHit(self._objects[result.document.id], result.document.id, self.path,
                         self._values[result.document.id], result.score, result.algorithm)
            for result in self._text.search(query, algorithm=algorithm, limit=limit, min_score=min_score)
        ]

    def contains(self, needle: Any, *, case_sensitive: Optional[bool] = None) -> List[DDMSearchHit]:
        """Return whether a value/substring lies within the represented range or indexed path data.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        needle : Any
            Value supplied for ``needle`` according to the DDMPathIndex contract.
        case_sensitive : Optional[bool] (default: ``None``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``List[DDMSearchHit]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        cs = self.case_sensitive if case_sensitive is None else case_sensitive
        q = _norm(needle, cs)
        out = []
        for key, value in self._values.items():
            if q in _norm(value, cs):
                out.append(DDMSearchHit(self._objects[key], key, self.path, value, 1.0, "contains"))
        return out

    def stats(self) -> Dict[str, int]:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`DDMPathIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return {
            "values": len(self._values),
            "exact_keys": len(self._exact),
            "numeric_values": len(self._numbers),
            "string_values": len(self._strings),
        }


class DDMCompositeIndex:
    """Composite exact DDM index.
    
    Overview
    --------
    ``DDMCompositeIndex`` provides hash lookup over a tuple of multiple dotted-path values.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for repeated equality queries that constrain the same field combination.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    find.
    """

    __slots__ = ("paths", "_objects", "_index")

    def __init__(self, paths: Sequence[str], entries: Sequence[Tuple[Any, Any]],
                 *, objects: Optional[Mapping[Any, Any]] = None):
        """Initialize a new DDMCompositeIndex instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DDMCompositeIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        paths : Sequence[str]
            Dotted paths participating in an index/composite operation.
        entries : Sequence[Tuple[Any, Any]]
            Initial autocomplete/index entries.
        objects : Optional[Mapping[Any, Any]] (default: ``None``)
            Optional shared key-to-object mapping reused by DDM indexes.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if not paths:
            raise ValueError("paths cannot be empty")
        self.paths = tuple(paths)
        self._objects = dict(entries) if objects is None else objects
        self._index: Dict[Tuple[Any, ...], List[Any]] = {}
        missing = object()
        for key, item in entries:
            values = tuple(_native.ddm_get_path(item, path, missing) for path in self.paths)
            if any(value is missing for value in values):
                continue
            self._index.setdefault(tuple(_index_key(v) for v in values), []).append(key)

    def find(self, *values: Any) -> List[Any]:
        """Return tree/search records that satisfy a predicate or query.
        
        Details
        -------
        This method belongs to :class:`DDMCompositeIndex` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *values : Any
            Input iterable, mapping values or composite lookup values.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if len(values) != len(self.paths):
            raise ValueError(f"expected {len(self.paths)} values")
        return [self._objects[key] for key in self._index.get(tuple(_index_key(v) for v in values), ())]


class DDMSearchEngine:
    """Nested structured-data search engine.
    
    Overview
    --------
    ``DDMSearchEngine`` provides shared record snapshot plus reusable exact/range/text/composite dotted-path indexes and scan fallback.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for large DDM-compatible datasets and queries such as profile.name or economy.balance.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    refresh, invalidate, create_index, create_indexes, create_composite_index, find, find_one, exists, count, between, text, composite, where, order_by, values, stats.
    
    Index strategy
    --------------
    The engine shares one source/object snapshot across path/composite indexes to avoid repeating the same object map for every indexed field. Exact indexes use hash maps, range-friendly values use sorted data, and optional text indexes use YoungLion SearchIndex.
    
    Example::
    
        engine = DDMSearchEngine(users).create_indexes(
            "id", "profile.name", "profile.age"
        )
        alice = engine.find_one("profile.name", "Alice")
        adults = engine.between("profile.age", 18, 65)
    """

    OPS = {"eq", "ne", "lt", "le", "lte", "gt", "ge", "gte", "contains", "prefix", "startswith", "endswith", "in", "is_none", "not_none"}

    __slots__ = (
        "source", "case_sensitive", "_indexes", "_composite", "_dirty", "_all_dirty",
        "_entry_cache", "_item_cache", "_object_cache",
    )

    def __init__(self, source: Any, *, case_sensitive: bool = False):
        """Initialize a new DDMSearchEngine instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : Any
            Source path, collection or transfer identifier.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self.source = source
        self.case_sensitive = bool(case_sensitive)
        self._indexes: Dict[str, DDMPathIndex] = {}
        self._composite: Dict[Tuple[str, ...], DDMCompositeIndex] = {}
        self._dirty: set[str] = set()
        self._all_dirty = False
        self._entry_cache: Optional[List[Tuple[Any, Any]]] = None
        self._item_cache: Optional[List[Any]] = None
        self._object_cache: Optional[Dict[Any, Any]] = None

    def _entries(self) -> List[Tuple[Any, Any]]:
        if self._entry_cache is not None:
            return self._entry_cache
        source = self.source
        # Normal mappings and DictDDM preserve application keys.
        if isinstance(source, Mapping):
            entries = list(source.items())
        elif hasattr(source, "_items_snapshot"):
            items = source._items_snapshot()
            entries = list(enumerate(items))
        else:
            items = list(source)
            entries = list(enumerate(items))
        self._entry_cache = entries
        self._item_cache = [item for _, item in entries]
        self._object_cache = dict(entries)
        return entries

    def _items(self) -> List[Any]:
        if self._item_cache is None:
            self._entries()
        return self._item_cache or []

    def _objects(self) -> Dict[Any, Any]:
        if self._object_cache is None:
            self._entries()
        return self._object_cache or {}

    def _clear_record_store(self) -> None:
        self._entry_cache = None
        self._item_cache = None
        self._object_cache = None

    def refresh(self) -> "DDMSearchEngine":
        """Rebuild class-specific cached/indexed state from the current source.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'DDMSearchEngine'`` result described by the method semantics.
        
        Notes
        -----
        Refresh rebuilds the source snapshot and cached indexes. Use it after structural/external source mutations that the engine could not observe automatically.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        paths = list(self._indexes)
        composites = list(self._composite)
        self._indexes.clear(); self._composite.clear(); self._dirty.clear(); self._all_dirty = False
        self._clear_record_store()
        for path in paths: self.create_index(path)
        for paths_ in composites: self.create_composite_index(*paths_)
        return self

    def invalidate(self, paths: Optional[Iterable[str]] = None) -> None:
        """Invalidate cached lazy fields so they will be recomputed on next access.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        paths : Optional[Iterable[str]] (default: ``None``)
            Dotted paths participating in an index/composite operation.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Path-only invalidation allows targeted indexes to be rebuilt while retaining the shared record snapshot when source structure itself has not changed.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        if paths is None:
            self._all_dirty = True
            self._clear_record_store()
            return
        changed = tuple(paths)
        for indexed in self._indexes:
            if any(indexed == path or indexed.startswith(path + ".") or path.startswith(indexed + ".") for path in changed):
                self._dirty.add(indexed)
        for composite in self._composite:
            if any(any(p == path or p.startswith(path + ".") or path.startswith(p + ".") for p in composite) for path in changed):
                self._all_dirty = True

    def create_index(self, path: str, *, text: bool = True) -> DDMPathIndex:
        """Create and cache an index for one dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        text : bool (default: ``True``)
            Text/content input.
        
        Returns
        -------
        ``DDMPathIndex`` result described by the method semantics.
        
        Notes
        -----
        Index construction has an upfront time/memory cost but can turn repeated exact queries into hash lookups and repeated ranges into sorted-index operations.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        index = DDMPathIndex(path, self._entries(), text=text, case_sensitive=self.case_sensitive, objects=self._objects())
        self._indexes[path] = index; self._dirty.discard(path)
        return index

    index = create_index

    def create_indexes(self, *paths: str, text: bool = True) -> "DDMSearchEngine":
        """Create indexes for several dotted paths and return the engine for fluent setup.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        text : bool (default: ``True``)
            Text/content input.
        
        Returns
        -------
        ``'DDMSearchEngine'`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        for path in paths: self.create_index(path, text=text)
        return self

    def create_composite_index(self, *paths: str) -> DDMCompositeIndex:
        """Create a reusable exact index over a tuple of dotted paths.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        
        Returns
        -------
        ``DDMCompositeIndex`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        key = tuple(paths)
        index = DDMCompositeIndex(key, self._entries(), objects=self._objects())
        self._composite[key] = index
        return index

    def _ensure(self, path: str) -> DDMPathIndex:
        if self._all_dirty:
            self.refresh()
        if path not in self._indexes or path in self._dirty:
            return self.create_index(path)
        return self._indexes[path]

    def find(self, path: str, value: Any = None, *, op: str = "eq", limit: Optional[int] = None,
             use_index: bool = True) -> List[Any]:
        """Return tree/search records that satisfy a predicate or query.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.
        use_index : bool (default: ``True``)
            Value supplied for ``use_index`` according to the DDMSearchEngine contract.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        op = op.lower()
        op = {"gte": "ge", "lte": "le"}.get(op, op)
        if use_index and op in {"eq", "prefix", "startswith", "contains"}:
            index = self._ensure(path)
            if op == "eq": hits = index.exact(value)
            elif op in {"prefix", "startswith"}: hits = index.prefix(str(value), limit=limit)
            else: hits = index.contains(value)
            result = [hit.item for hit in hits]
        elif use_index and op in {"lt", "le", "gt", "ge"}:
            index = self._ensure(path)
            if op == "lt": hits = index.range(None, value, include_max=False)
            elif op == "le": hits = index.range(None, value, include_max=True)
            elif op == "gt": hits = index.range(value, None, include_min=False)
            else: hits = index.range(value, None, include_min=True)
            result = [hit.item for hit in hits]
        else:
            native_op = "startswith" if op == "prefix" else op
            result = _native.batch_filter_path(self._items(), path, native_op, value)
        return result if limit is None else result[:max(0, int(limit))]

    def find_one(self, path: str, value: Any = None, *, op: str = "eq", default: Any = None,
                 use_index: bool = True) -> Any:
        """Return the first matching record for a dotted-path comparison or a default.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        use_index : bool (default: ``True``)
            Value supplied for ``use_index`` according to the DDMSearchEngine contract.
        
        Returns
        -------
        First matching source record, or the caller-provided default.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        rows = self.find(path, value, op=op, limit=1, use_index=use_index)
        return rows[0] if rows else default

    def exists(self, path: str, value: Any = None, *, op: str = "eq") -> bool:
        """Return whether any record satisfies the dotted-path comparison.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        ``True`` if at least one matching record exists.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self.find_one(path, value, op=op, default=None) is not None

    def count(self, path: str, value: Any = None, *, op: str = "eq") -> int:
        """Return the number of stored values or matching records, depending on the class.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        Number of records/fields matching the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return len(self.find(path, value, op=op))

    def between(self, path: str, minimum: Any, maximum: Any, *, include_min: bool = True,
                include_max: bool = True) -> List[Any]:
        """Return records whose dotted-path value falls within the requested bounds.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        minimum : Any
            Lower bound or minimum accepted value.
        maximum : Any
            Upper bound or maximum accepted value.
        include_min : bool (default: ``True``)
            Whether a lower range bound is inclusive.
        include_max : bool (default: ``True``)
            Whether an upper range bound is inclusive.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return [hit.item for hit in self._ensure(path).range(minimum, maximum, include_min=include_min, include_max=include_max)]

    def text(self, path: str, query: str, *, algorithm: Union[SearchAlgorithm, str] = SearchAlgorithm.HYBRID,
             limit: Optional[int] = 10, min_score: float = 0.0, hits: bool = False):
        """Perform the ``text`` operation for DDMSearchEngine.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        limit : Optional[int] (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        min_score : float (default: ``0.0``)
            Minimum normalized/relevance score required for returned results.
        hits : bool (default: ``False``)
            Whether DDM text search returns DDMSearchHit metadata instead of only source objects.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        results = self._ensure(path).text(query, algorithm=algorithm, limit=limit, min_score=min_score)
        return results if hits else [result.item for result in results]

    def composite(self, paths: Sequence[str], values: Sequence[Any]) -> List[Any]:
        """Query a previously built composite dotted-path index.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        paths : Sequence[str]
            Dotted paths participating in an index/composite operation.
        values : Sequence[Any]
            Input iterable, mapping values or composite lookup values.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        key = tuple(paths)
        if self._all_dirty:
            self.refresh()
        index = self._composite.get(key) or self.create_composite_index(*key)
        return index.find(*values)

    @staticmethod
    def _parse_lookup(name: str) -> Tuple[str, str]:
        parts = name.split("__")
        if parts[-1] in {"eq", "ne", "lt", "le", "lte", "gt", "ge", "gte", "contains", "prefix", "startswith", "endswith", "in", "is_none", "not_none"}:
            op = parts.pop()
        else:
            op = "eq"
        return ".".join(parts), op

    def where(self, **lookups: Any) -> List[Any]:
        """Apply one or more structured lookup expressions and return matching records.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        **lookups : Any
            Structured lookup expressions supplied as keyword arguments.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        
        Example::
        
            active_adults = engine.where(
                active__eq=True,
                profile__age__gte=18,
            )
        """
        if not lookups:
            return list(self._items())
        result: Optional[List[Any]] = None
        for lookup, expected in lookups.items():
            path, op = self._parse_lookup(lookup)
            matches = self.find(path, expected, op=op)
            if result is None:
                result = matches
            else:
                allowed = {id(item) for item in matches}
                result = [item for item in result if id(item) in allowed]
            if not result: break
        return result or []

    query = where

    def order_by(self, path: str, *, reverse: bool = False, missing_last: bool = True) -> List[Any]:
        """Return source records ordered by a dotted-path value.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        missing_last : bool (default: ``True``)
            Whether records lacking the sort path should be placed after records with values.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return _native.batch_sort_path(self._items(), path, reverse=reverse, missing_last=missing_last)

    def values(self, path: str, default: Any = None) -> List[Any]:
        """Return a dynamic view or collection of stored values.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return _native.batch_get_path(self._items(), path, default)

    def stats(self) -> Dict[str, Any]:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`DDMSearchEngine` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return {
            "records": len(self._items()),
            "indexes": {path: index.stats() for path, index in self._indexes.items()},
            "composite_indexes": [list(paths) for paths in self._composite],
            "dirty_indexes": sorted(self._dirty),
        }


_SEARCH_MISSING = object()


class ApplicationSearch:
    """Application-facing search backend.
    
    Overview
    --------
    ``ApplicationSearch`` provides document CRUD, ranked results, payload retrieval, autocomplete, facets and statistics.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for command palettes, help centers, settings, product/catalog and local app search.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    add, update, remove, search_results, search, suggest, facet, stats.
    
    Example::
    
        search = ApplicationSearch()
        search.add("settings.theme", "Theme", "Change application appearance",
                   tags=["settings", "appearance"], payload={"route": "/theme"})
        routes = search.search("appearance")
        suggestions = search.suggest("the")
    """

    def __init__(self, *, case_sensitive: bool = False):
        """Initialize a new ApplicationSearch instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        self._case_sensitive = bool(case_sensitive)
        self.index = SearchIndex(case_sensitive=case_sensitive)
        self.autocomplete = AutocompleteIndex(case_sensitive=case_sensitive)
        self._payloads: Dict[Hashable, Any] = {}
        self._titles: Dict[Hashable, Tuple[str, float]] = {}

    def _rebuild_autocomplete(self) -> None:
        self.autocomplete = AutocompleteIndex(case_sensitive=self._case_sensitive)
        for doc_id, (title, weight) in self._titles.items():
            self.autocomplete.add(title, doc_id, weight)

    def add(self, doc_id: Hashable, title: str, body: str = "", *, tags: Iterable[str] = (),
            fields: Optional[Mapping[str, Any]] = None, payload: Any = None, autocomplete_weight: float = 1.0) -> SearchDocument:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        title : str
            Value supplied for ``title`` according to the ApplicationSearch contract.
        body : str (default: ``''``)
            Plain-text message body.
        tags : Iterable[str] (default: ``()``)
            Value supplied for ``tags`` according to the ApplicationSearch contract.
        fields : Optional[Mapping[str, Any]] (default: ``None``)
            Field names or field mapping used for structured document data.
        payload : Any (default: ``None``)
            Application value associated with an indexed entry/document.
        autocomplete_weight : float (default: ``1.0``)
            Weight assigned to the document title in autocomplete ranking.
        
        Returns
        -------
        ``SearchDocument`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        
        Example::
        
            search.add(
                "cmd.settings", "Settings", "Open application settings",
                tags=["config"], fields={"category": "system"},
                payload={"route": "/settings"},
            )
        """
        title = str(title)
        body = str(body)
        fields_dict = dict(fields or {})
        replacing = doc_id in self.index._docs
        document = SearchDocument(
            doc_id,
            f"{title} {body}".strip(),
            metadata={"title": title, "body": body, "return": payload},
            tags=tuple(tags),
            fields=fields_dict,
        )
        self.index.add(document)
        self._payloads[doc_id] = payload
        self._titles[doc_id] = (title, float(autocomplete_weight))
        if replacing:
            self._rebuild_autocomplete()
        else:
            self.autocomplete.add(title, doc_id, autocomplete_weight)
        return document

    def update(self, doc_id: Hashable, *, title: Optional[str] = None, body: Optional[str] = None,
               tags: Optional[Iterable[str]] = None, fields: Optional[Mapping[str, Any]] = None, payload: Any = _SEARCH_MISSING,
               autocomplete_weight: Optional[float] = None) -> SearchDocument:
        """Update top-level fields from mapping arguments and keyword values.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        title : Optional[str] (default: ``None``)
            Value supplied for ``title`` according to the ApplicationSearch contract.
        body : Optional[str] (default: ``None``)
            Plain-text message body.
        tags : Optional[Iterable[str]] (default: ``None``)
            Value supplied for ``tags`` according to the ApplicationSearch contract.
        fields : Optional[Mapping[str, Any]] (default: ``None``)
            Field names or field mapping used for structured document data.
        payload : Any (default: ``_SEARCH_MISSING``)
            Application value associated with an indexed entry/document.
        autocomplete_weight : Optional[float] (default: ``None``)
            Weight assigned to the document title in autocomplete ranking.
        
        Returns
        -------
        ``SearchDocument`` result described by the method semantics.
        
        Notes
        -----
        Updates rebuild the affected indexed/autocomplete state so stale title/body suggestions are not retained.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        old = self.index._docs[doc_id]
        old_title = str(old.metadata.get("title", ""))
        old_body = str(old.metadata.get("body", ""))
        new_title = old_title if title is None else str(title)
        new_body = old_body if body is None else str(body)
        new_payload = self._payloads.get(doc_id) if payload is _SEARCH_MISSING else payload
        document = SearchDocument(
            doc_id,
            f"{new_title} {new_body}".strip(),
            metadata={"title": new_title, "body": new_body, "return": new_payload},
            tags=old.tags if tags is None else tuple(tags),
            fields=old.fields if fields is None else dict(fields),
        )
        self.index.add(document)
        self._payloads[doc_id] = new_payload
        previous_weight = self._titles.get(doc_id, (old_title, 1.0))[1]
        self._titles[doc_id] = (new_title, previous_weight if autocomplete_weight is None else float(autocomplete_weight))
        self._rebuild_autocomplete()
        return document

    def remove(self, doc_id: Hashable) -> bool:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        removed = self.index.remove(doc_id)
        if removed:
            self._payloads.pop(doc_id, None)
            self._titles.pop(doc_id, None)
            self._rebuild_autocomplete()
        return removed

    def search_results(self, query: Union[str, SearchQuery], **kwargs: Any) -> List[SearchResult]:
        """Return rich SearchResult-style objects rather than only application payloads/values.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[SearchResult]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self.index.search(query, **kwargs)

    def search(self, query: Union[str, SearchQuery], **kwargs: Any) -> List[Any]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        results = self.search_results(query, **kwargs)
        return [self._payloads.get(result.document.id, result.document) for result in results]

    def suggest(self, prefix: str, *, limit: int = 10, fuzzy: bool = True) -> List[AutocompleteEntry]:
        """Return ranked autocomplete candidates for a prefix with optional fuzzy fallback.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : int (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        fuzzy : bool (default: ``True``)
            Whether suggestions may use fuzzy fallback.
        
        Returns
        -------
        ``List[AutocompleteEntry]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self.autocomplete.suggest(prefix, limit=limit, fuzzy_fallback=fuzzy)

    def facet(self, field: str, *, query: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple[Any, int]]:
        """Count values for one field, optionally restricted to documents matching a query.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        field : str
            Field name used for a facet or structured operation.
        query : Optional[str] (default: ``None``)
            Search text, structured query or SQL/XML expression according to the method.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.
        
        Returns
        -------
        ``List[Tuple[Any, int]]`` result described by the method semantics.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        docs = self.index._docs.values() if query is None else (result.document for result in self.index.search(query, limit=None))
        counts = Counter(doc.fields.get(field) for doc in docs if field in doc.fields)
        rows = counts.most_common()
        return rows if limit is None else rows[:max(0, int(limit))]

    def stats(self) -> SearchStats:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`ApplicationSearch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        
        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        return self.index.stats()


# Descriptive aliases for application-facing APIs.
SearchEngine = ApplicationSearch
DDMIndex = DDMPathIndex


# Public exports added by the v0.1 search expansion.
__all__ += [
    "DDMSearchHit", "DDMPathIndex", "DDMCompositeIndex", "DDMSearchEngine",
    "ApplicationSearch", "SearchEngine", "DDMIndex",
]
