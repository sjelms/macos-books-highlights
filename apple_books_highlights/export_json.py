"""
Handles the creation of the enriched JSON file.
"""
import json
import pathlib
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

        # Create Pydantic models
        metadata = Metadata(**normalized_meta)
        parsed_annotations = [Annotation.parse_obj(a) for a in annotations]

        enriched_data = EnrichedJSON(metadata=metadata, annotations=parsed_annotations)

        # Construct filename and write to JSON file
        filename = f"{metadata.citation_key} {metadata.entry_type}-ab.json"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Use .dict() for Pydantic v1, .model_dump() for v2. Assuming v1 for now.
            # Using by_alias=True to respect the 'selected_text' alias.
            f.write(enriched_data.model_dump_json(by_alias=True, indent=2))

        return output_path