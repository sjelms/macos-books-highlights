"""
Handles the creation of the enriched JSON file.
"""
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from . import bib
from . import booksdb

class Annotation(BaseModel):
    """Data model for a single highlight annotation."""
    highlight: Optional[str] = Field(None, alias='selected_text')
    note: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = Field(None, alias='style')
    chapter: Optional[str] = None

class Metadata(BaseModel):
    """Data model for the book's metadata."""
    citation_key: str
    title: str
    authors: List[str]
    editors: List[str]
    year: int
    doi: str
    url: str
    entry_type: str
    short_title: str

class EnrichedJSON(BaseModel):
    """Top-level data model for the enriched JSON file."""
    metadata: Metadata
    annotations: List[Annotation]

def create_enriched_json(
    book_title: str,
    book_author: str,
    annotations_data: List[Dict[str, Any]],
    bib_database: bib.bibtexparser.bibdatabase.BibDatabase,
    output_path: str
):
    """
    Creates an enriched JSON file for a given book.

    Args:
        book_title: The title of the book from Apple Books.
        book_author: The author of the book from Apple Books.
        annotations_data: A list of raw annotation data from booksdb.
        bib_database: The parsed BibTeX database.
        output_path: The path to save the enriched JSON file.
    """
    # Find the best matching BibTeX entry
    bib_entry = bib.find_bibtex_entry(book_title, [book_author], bib_database)

    if not bib_entry:
        print(f"Warning: No BibTeX entry found for '{book_title}'. Skipping.")
        return

    # Normalize metadata from the BibTeX entry
    normalized_meta = bib.normalize_meta(bib_entry)

    # Create Pydantic models
    metadata = Metadata(**normalized_meta)
    annotations = [Annotation.parse_obj(a) for a in annotations_data]

    enriched_data = EnrichedJSON(metadata=metadata, annotations=annotations)

    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_data.dict(by_alias=True), f, indent=2)

    print(f"Successfully created enriched JSON for '{book_title}' at {output_path}")

