"""
Handles the export of enriched annotations to a Readwise-ready CSV file.
"""
import csv
import json
import pathlib

class CsvExporter:
    """Orchestrates the creation of a Readwise-compatible CSV file."""

    def __init__(self, output_dir: str):
        """
        Initializes the exporter with the output directory.

        Args:
            output_dir: The directory where CSV files will be saved.
        """
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, enriched_json_path: str):
        """
        Creates a Readwise-ready CSV file from an enriched JSON file.

        Args:
            enriched_json_path: Path to the enriched JSON file.
        """
        with open(enriched_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metadata = data.get("metadata", {})
        annotations = data.get("annotations", [])

        if not annotations:
            return

        # Construct filename
        filename = f"{metadata['citation_key']} {metadata['entry_type']}-ab.csv"
        output_path = self.output_dir / filename

        # Readwise required headers
        headers = ["Title", "Author", "Category", "Source URL", "Highlight", "Note", "Location"]

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for annot in annotations:
                source_url = ""
                if metadata.get("doi"):
                    source_url = f'https://doi.org/{metadata.get("doi")}'
                elif metadata.get("url"):
                    source_url = metadata.get("url")

                writer.writerow({
                    "Title": metadata.get("title", ""),
                    "Author": ", ".join(metadata.get("authors", [])),
                    "Category": "books",
                    "Source URL": source_url,
                    "Highlight": annot.get("highlight", ""),
                    "Note": annot.get("note", ""),
                    "Location": annot.get("chapter", ""),
                })
