"""
Handles the export of enriched annotations to a Readwise-ready CSV file.
"""
import csv
import json

def create_readwise_csv(json_path: str, output_path: str):
    """
    Creates a Readwise-ready CSV file from an enriched JSON file.

    Args:
        json_path: Path to the enriched JSON file.
        output_path: Path to write the output CSV file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)

    metadata = enriched_data.get("metadata", {})
    annotations = enriched_data.get("annotations", [])

    if not annotations:
        print(f"No annotations found in {json_path}. Skipping CSV export.")
        return

    # Readwise required headers
    headers = ["Title", "Author", "Category", "Source URL", "Highlight", "Note", "Location"]

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for annot in annotations:
            # Prioritize DOI for Source URL, then fallback to URL
            source_url = ""
            if metadata.get("doi"):
                source_url = f'https://doi.org/{metadata.get("doi")}'
            elif metadata.get("url"):
                source_url = metadata.get("url")

            writer.writerow({
                "Title": metadata.get("title", ""),
                "Author": ", ".join(metadata.get("authors", [])),
                "Category": "books",  # Defaulting to books for this project
                "Source URL": source_url,
                "Highlight": annot.get("highlight", ""),
                "Note": annot.get("note", ""),
                "Location": annot.get("chapter", ""),
            })

    print(f"Successfully exported {len(annotations)} highlights to {output_path}")