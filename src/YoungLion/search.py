"""
Do you want to integrate an advanced search system into your programs? 
This module is for you! Without dealing with complex algorithms, 
enter your data and search criteria, and the module will quickly find the most relevant results. 
Save time and money, and experience a high-performance search experience.
"""
import re
import itertools
from typing import *
import difflib
class GenerateTags:
    """
    A class for generating relevant tags from a given list of keywords or a keyword phrase.
    
    Features:
    - Accepts both a string or a list of keywords.
    - Generates unique keyword combinations (from single words up to full phrase).
    - Supports permutations (reordering matters).
    - Provides case normalization (lowercase, uppercase).
    - Cleans special characters (optional).
    - Allows min/max word limits for tag generation.
    - Supports predefined keyword replacements (e.g., "Minecraft" → "MC"), keeping both versions.
    - Supports stop-word filtering (removing unnecessary words).
    """

    def __init__(self, terms:str|list, lowercase:bool=True, clean_special_chars:bool=True, min_words:int=1, max_words:int=None, replacements:dict=None, stop_words:list=None):
        """
        Initializes the GenerateTags instance.

        :param terms: (str or list) The main keyword(s) to generate tags from.
        :param lowercase: (bool) Whether to convert all tags to lowercase. Default is True.
        :param clean_special_chars: (bool) Remove special characters from terms. Default is True.
        :param min_words: (int) Minimum words in a tag. Default is 1.
        :param max_words: (int) Maximum words in a tag. If None, it takes the length of terms.
        :param replacements: (dict) A dictionary to replace specific words (e.g., {"Minecraft": "MC"}), keeping both versions.
        :param stop_words: (list) List of words to exclude from the tag generation.
        """
        if isinstance(terms, str):
            self.terms = terms.split()  # Convert string to list of words
        elif isinstance(terms, list):
            self.terms = terms
        else:
            raise ValueError("Terms must be either a string or a list of words.")

        # Optional settings
        self.lowercase = lowercase
        self.clean_special_chars = clean_special_chars
        self.min_words = min_words
        self.max_words = max_words or len(self.terms)  # Default max words to full phrase
        self.replacements = replacements or {}
        self.stop_words = set(stop_words or [])

        # Apply cleaning and normalization
        self.terms = self._preprocess_terms(self.terms)

    def _preprocess_terms(self, terms) -> list:
        """
        Cleans and normalizes terms according to user settings.
        
        - Removes special characters if enabled.
        - Converts to lowercase if enabled.
        - Applies keyword replacements if provided.
        - Removes stop words if provided.
        """
        cleaned_terms = []

        for term in terms:
            if self.clean_special_chars:
                term = re.sub(r'[^a-zA-Z0-9 ]', '', term)  # Remove special characters
            
            if self.lowercase:
                term = term.lower()

            if term in self.stop_words:
                continue  # Skip stop words

            cleaned_terms.append(term)

        return cleaned_terms

    def _apply_replacements(self, terms) -> list:
        """
        Applies replacements while keeping both original and replaced words.
        """
        expanded_terms = []

        for term in terms:
            if term in self.replacements:
                expanded_terms.append([term, self.replacements[term]])  # Keep both versions
            else:
                expanded_terms.append([term])  # No replacement, keep as is

        # Generate all possible combinations of replacements
        return [list(combo) for combo in itertools.product(*expanded_terms)]

    def _generate_combinations(self) -> list:
        """
        Generates all possible keyword combinations and permutations within the min/max word range.
        """
        tags = set()  # Use a set to ensure uniqueness

        # Generate expanded term lists (to handle replacements)
        term_variants = self._apply_replacements(self.terms)

        for variant in term_variants:
            for i in range(self.min_words, self.max_words + 1):
                for combo in itertools.combinations(variant, i):
                    tags.add(" ".join(combo))  # Standard combination
                    tags.add(" ".join(combo[::-1]))  # Reversed order
                
                    # Generate permutations (when order matters)
                    for perm in itertools.permutations(combo):
                        tags.add(" ".join(perm))

        return sorted(tags)  # Return sorted list for consistency

    def get_tags(self) -> list:
        """
        Returns the generated tags.
        """
        return self._generate_combinations()
    
class SearchData:
    """
    A custom data structure for organizing search data.

    This class acts like a dictionary where tags are mapped to return values.
    """

    def __init__(self, data: List[Dict[str, Any]]):
        """
        Initializes the SearchData instance.

        :param data: (List[Dict]) A list of dictionaries containing 'tags' and 'return' values.
        """
        self._structured_data: Dict[str, List[Any]] = {}
        self._process_data(data)

    def _process_data(self, data: List[Dict[str, Any]]) -> None:
        """Processes the input data and structures it."""
        for entry in data:
            tags = entry.get('tags', [])
            return_value = entry.get('return')

            if not tags or return_value is None:
                continue  # Skip invalid entries

            for tag in tags:
                if tag not in self._structured_data:
                    self._structured_data[tag] = []
                self._structured_data[tag].append(return_value) 
    def get_tags(self) -> list:
        """ Returns a list of all available tags in the dataset. """
        return list(self._structured_data.keys())
    def get(self, tag: str) -> List[Any]:
        """
        Retrieves the return values associated with a specific tag.

        :param tag: (str) The tag to look up.
        :return: (List) A list of return values related to the tag.
        """
        return self._structured_data.get(tag, []) 

    def __getitem__(self, tag: str) -> List[Any]:
        """Allows dictionary-like access to search data."""
        return self.get(tag)

    def __contains__(self, tag: str) -> bool:
        """Allows checking if a tag exists in the data."""
        return tag in self._structured_data

    def __repr__(self) -> str:
        """String representation for debugging."""
        return repr(self._structured_data)
    

class Search:
    """
    A powerful search engine for retrieving data based on keyword tags.
    
    Attributes:
        sdata (SearchData): The structured data containing tags and return values.
        only_tag (bool): If True, only exact tag matches will be considered.
    """

    def __init__(self, sdata: "SearchData", only_tag: bool = False):
        """
        Initializes the Search class with structured data and a search mode.
        
        Args:
            sdata (SearchData): The structured data containing tags and return values.
            only_tag (bool): If True, only exact tag matches will be considered.
        """
        self.sdata = sdata
        self.only_tag = only_tag  

    def search(self, query: str) -> List[Any]:
        """
        Searches for relevant tags based on the given query and retrieves associated return values.

        Args:
            query (str): The search query (e.g., a keyword or phrase).

        Returns:
            List[Any]: A list of associated return values for the matched tags.
        """
        matched_tags = self._find_matching_tags(query)
        results = self._gather_results(matched_tags)
        return results

    def _find_matching_tags(self, query: str) -> List[str]:
        """
        Finds the most relevant tags based on the search query.

        Args:
            query (str): The search query.

        Returns:
            List[str]: A list of matched tags.
        """
        existing_tags = self.sdata.get_tags()

        if self.only_tag:
            return [tag for tag in existing_tags if tag == query]

        close_matches = difflib.get_close_matches(query, existing_tags, n=5, cutoff=0.6)
        
        if query in existing_tags:
            close_matches.insert(0, query)

        return list(set(close_matches)) 

    def _gather_results(self, matched_tags: List[str]) -> List[Any]:
        """
        Collects all return values for the matched tags.

        Args:
            matched_tags (List[str]): The tags that matched the search query.

        Returns:
            List[Any]: A combined list of all relevant return values.
        """
        results = []
        for tag in matched_tags:
            results.extend(self.sdata.get(tag))
        return results