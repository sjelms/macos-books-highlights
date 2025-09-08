"""
Handles the creation of the enriched JSON file.
"""
import json
import pathlib
import html
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .bib import BibTexLibrarian

# Pydantic Models for data validation and serialization
class Annotation(BaseModel):
    """Data model for a single highlight annotation."""
    annotation_id: str
    highlight: Optional[str] = Field(None, alias='selected_text')
    note: Optional[str] = None
    location: Optional[str] = None
    color: Optional[int] = Field(None, alias='style')
    chapter: Optional[str] = None
    modified_date: Any = Field(None, alias='modified_date')

class Metadata(BaseModel):
    """Data model for the book's metadata."""
    asset_id: str
    citation_key: str
    title: str
    authors: List[str]
    editors: List[str]
    year: Any
    doi: Optional[str] = None
    url: Optional[str] = None
    entry_type: str
    short_title: str

class EnrichedJSON(BaseModel):
    """Top-level data model for the enriched JSON file."""
    metadata: Metadata
    annotations: List[Annotation]

class JsonExporter:
    """Orchestrates the creation of an enriched JSON file for a book."""

    def __init__(self, output_dir: str):
        """
        Initializes the exporter with the output directory.

        Args:
            output_dir: The directory where JSON files will be saved.
        """
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_text(self, s: str) -> str:
        if s is None:
            return ""
        # HTML entities → characters (e.g., &amp; → &)
        s = html.unescape(str(s))
        # Normalize newlines and remove carriage returns
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        # Normalize spaces
        s = s.replace("\xa0", " ")  # non-breaking space
        s = s.replace("\u200b", "")  # zero-width space
        s = s.replace("\ufeff", "")  # BOM
        s = s.replace("\u00ad", "")  # soft hyphen
        # Trim each line and collapse intra-line runs of spaces/tabs, then join with a single space
        lines = [re.sub(r"[\t ]+", " ", ln.strip()) for ln in s.split("\n")]
        s = " ".join([ln for ln in lines if ln])
        return s.strip()

    def export(self, annotations: List[Dict[str, Any]], bib_librarian: BibTexLibrarian) -> Optional[pathlib.Path]:
        """
        Creates and saves an enriched JSON file for a given book.

        Args:
            annotations: A list of raw annotation data for a single book from booksdb.
            bib_librarian: An initialized BibTexLibrarian instance.

        Returns:
            The path to the created JSON file, or None if no BibTeX match was found.
        """
        if not annotations:
            return None

        first_annotation = annotations[0]
        book_title = first_annotation.get('title')
        book_author = first_annotation.get('author')
        asset_id = first_annotation.get('asset_id')

        # Find the best matching BibTeX entry
        bib_entry = bib_librarian.find_bibtex_entry(book_title, [book_author])

        if not bib_entry:
            return None

        # Normalize metadata from the BibTeX entry
        normalized_meta = bib_librarian.normalize_meta(bib_entry)
        normalized_meta['asset_id'] = asset_id

        # Sanitize text fields before validation
        for ann in annotations:
            ann['selected_text'] = self._sanitize_text(ann.get('selected_text'))
            ann['note'] = self._sanitize_text(ann.get('note'))

        # Create Pydantic models
        metadata = Metadata(**normalized_meta)
        parsed_annotations = [Annotation.parse_obj(a) for a in annotations]

        enriched_data = EnrichedJSON(metadata=metadata, annotations=parsed_annotations)

        # Construct filename and write to JSON file
        filename = f"{metadata.citation_key} {metadata.entry_type}-ab.json"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enriched_data.model_dump_json(indent=2))

        return output_path
