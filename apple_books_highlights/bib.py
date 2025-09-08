"""
Handles BibTeX parsing and metadata matching.
"""
import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from thefuzz import fuzz
from typing import List, Optional, Dict, Any

class BibTexLibrarian:
    """Manages loading, searching, and normalizing a BibTeX library."""

    def __init__(self, bibtex_path: str):
        """
        Initializes the librarian and loads the BibTeX database.

        Args:
            bibtex_path: The path to the .bib file.
        """
        self.db = self._load_bibtex(bibtex_path)

    def _load_bibtex(self, bibtex_path: str) -> bibtexparser.bibdatabase.BibDatabase:
        """
        Loads and parses a BibTeX file.
        """
        with open(bibtex_path, 'r', encoding='utf-8') as bibtex_file:
            parser = BibTexParser(common_strings=True)
            parser.customization = convert_to_unicode
            return bibtexparser.load(bibtex_file, parser=parser)

    def _normalize_initials(self, name: str) -> str:
        return re.sub(r'\b([A-Z])\.\b', r'\1', name)

    def _strip_braces(self, text: str) -> str:
        return text.replace('{', '').replace('}', '')

    def _parse_names(self, field_value: str) -> List[str]:
        if not field_value:
            return []
        raw = self._strip_braces(field_value.strip())
        parts = re.split(r"\s+and\s+", raw)
        people: List[str] = []
        for p in parts:
            name = p.strip()
            if not name:
                continue
            last_first = [s.strip() for s in name.split(',', 1)]
            if len(last_first) == 2:
                full_name = f"{last_first[1]} {last_first[0]}".strip()
            else:
                full_name = last_first[0]
            full_name = re.sub(r"\s+", " ", full_name)
            full_name = self._normalize_initials(full_name)
            people.append(full_name)
        return people

    def _get_authors_from_entry(self, entry: Dict[str, Any]) -> List[str]:
        return self._parse_names(entry.get('author', ''))

    def _get_editors_from_entry(self, entry: Dict[str, Any]) -> List[str]:
        return self._parse_names(entry.get('editor', ''))

    def find_bibtex_entry(
        self, title: str, authors: List[str], title_threshold: int = 80, author_threshold: int = 80
    ) -> Optional[Dict[str, Any]]:
        """
        Finds the best matching BibTeX entry for a given book title and author.
        """
        best_match = None
        best_score = 0

        # Ensure authors is a list of strings
        authors_list = authors if isinstance(authors, list) else [authors] if authors else []

        for entry in self.db.entries:
            bib_title = entry.get('title', '')
            bib_authors = self._get_authors_from_entry(entry)

            title_score = fuzz.token_set_ratio(title, bib_title)

            if title_score > title_threshold:
                author_score = 0
                if authors_list and bib_authors:
                    author_str = " ".join(sorted(authors_list))
                    bib_author_str = " ".join(sorted(bib_authors))
                    author_score = fuzz.token_set_ratio(author_str, bib_author_str)
                
                # If there are no authors from the book data, a strong title match is sufficient
                if not authors_list or author_score > author_threshold:
                    total_score = title_score + author_score
                    if total_score > best_score:
                        best_score = total_score
                        best_match = entry
        return best_match

    def normalize_meta(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and normalizes metadata from a BibTeX entry.
        """
        raw_title = entry.get('title', '').strip()
        title = raw_title.replace(':', ' – ')
        title = re.sub(r"\s+[-–—]\s+", " – ", title)
        title = re.sub(r'\s+', ' ', title)
        title = title.rstrip('.,:; ')

        short_title_split = re.split(r'[:–-]', raw_title)
        short_title = short_title_split[0].strip() if short_title_split else title

        year = entry.get('year', '')
        match_year = re.search(r'\b(\d{4})\b', year)
        year_clean = match_year.group(1) if match_year else year

        return {
            'title': title,
            'short_title': short_title,
            'year': year_clean,
            'entry_type': entry.get('ENTRYTYPE', '').lower(),
            'citation_key': entry.get('ID', ''),
            'authors': self._get_authors_from_entry(entry),
            'editors': self._get_editors_from_entry(entry),
            'doi': entry.get('doi', ''),
            'url': entry.get('url', ''),
        }