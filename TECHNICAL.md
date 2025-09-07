# Technical Outline: Apple Books Highlight Extraction

This document outlines the technical plan for modifying this tool to extract Apple Books highlights and integrate them into the workflow established by the `pdf-highlight-extraction` project.

## 1. Project Goals

- **Extract:** Pull all highlights, notes, and available metadata (book title, author, chapter) from the Apple Books desktop application's database.
- **Enrich:** Augment the extracted data with rich bibliographic information by matching each book against a user-provided BibTeX library. A matching BibTeX entry is mandatory for processing.
- **Structure:** Create a single, enriched JSON file for each book. This file will serve as the canonical "source of truth" for all downstream processing.
- **Export:** Generate flexible output formats from the JSON data, specifically:
    - **CSV:** For data analysis or spreadsheet use.
    - **Markdown:** For integration into note-taking apps like Obsidian, replicating the precise formatting from the PDF project.
- **Modularize:** Refactor the existing codebase to separate data extraction from data processing and exporting, allowing for a more robust and maintainable pipeline.

## 2. Core Workflow

Python and packages `~/python-venv/`

The new workflow will be a multi-stage pipeline that transforms raw data from the Apple Books database into formatted, enriched notes.

1.  **Invocation:** The user runs a single command, e.g., `apple-books-highlights sync`.
2.  **Extraction:** The script connects to the Apple Books SQLite database and extracts all books and their associated annotations.
3.  **BibTeX Lookup:** For each book, the script searches the user's BibTeX library for a matching entry based on title and author. If no match is found, the script will issue a warning and skip the book.
4.  **Enrichment & Storage:** The script combines the extracted annotations with the metadata from the matched BibTeX entry and saves the result as an "enriched JSON" file. This file is the definitive record for the book.
5.  **Export:** The script reads the enriched JSON files and generates the final Markdown and CSV outputs.

## 3. Detailed Technical Outline

### Phase 1: Refactor for JSON-first Extraction

- **Modify `booksdb.py`:** Update the core extraction logic to fetch all available annotation data and return it as a Python dictionary or data class.
- **Create `json_handler.py`:** This new module will produce the "enriched JSON" file, orchestrating the BibTeX lookup and data combination.
- **Update `scripts/apple-books-highlights.py`:** The main entry point will be modified to drive the new pipeline.

### Phase 2: BibTeX Metadata Enrichment

- **Create `bibtex_lookup.py`:**
    - This module will manage all interactions with the BibTeX library (`bibtexparser` dependency).
    - **Metadata Normalization:** It will extract and normalize metadata from BibTeX entries:
        - `citation_key`: The BibTeX entry ID (e.g., `Doe2022-gs`).
        - `authors`/`editors`: Normalize names.
        - **Title (`title`):**
            - Replace colons with an en dash (` – `).
            - Standardize various dash types (`-`, `–`, `—`) to a single, spaced en dash.
            - Collapse multiple whitespace characters into a single space.
            - Strip trailing punctuation (e.g., `.` `,` `:` `;`).
        - **Short Title (`short_title`):**
            - Derive from the *raw* title by splitting on the first colon or dash and taking the first segment.
- **Configuration:** A `config.yaml` file will specify the path to the user's `.bib` file and output directories.

### Phase 3: Exporting from JSON

- **Create `exporters.py`:** This module will contain functions to generate the final output files from the enriched JSON, adhering to strict formatting rules.
- **Markdown Exporter:**
    - **YAML Front Matter:** Formatted precisely for Obsidian, with `citation-key` as `"[[@CitationKey]]"` and `type` as `"#entry_type-ab"`.
    - **Markdown Body:** Formatted with specific line breaks and structures for callouts and metadata.

## 4. Data Models & Formatting

### Enriched JSON Structure

This is the central data structure, holding all information needed for exporters.

```json
{
  "metadata": {
    "citation_key": "Harari2015-ab",
    "title": "Sapiens – A Brief History of Humankind",
    "authors": ["Yuval Noah Harari"],
    "editors": [],
    "year": 2015,
    "doi": "",
    "url": "",
    "entry_type": "book",
    "short_title": "Sapiens"
  },
  "annotations": [
    {
      "highlight": "This was the key to Sapiens’ success.",
      "note": "Very interesting example...",
      "location": "2: The Tree of Knowledge",
      "color": "yellow"
    }
  ]
}
```

### Markdown YAML Front Matter Example

This block must be formatted precisely, with no extra spaces around the citation key.

```yaml
---
title: "Sapiens – A Brief History of Humankind"
year: 2015
author-1: "[[Yuval Noah Harari]]"
citation-key: "[[@Harari2015-ab]]"
highlights: 1
type: "#book-ab"
aliases:
  - "Sapiens – A Brief History of Humankind"
  - "Sapiens"
---
```

### Markdown Body Formatting Example

This structure, including line breaks, is critical for Obsidian.

```markdown
# Highlights for [[@Harari2015-ab]]

- This was the key to Sapiens’ success.
> chapter: `2: The Tree of Knowledge`
> tags: #general-ab

>[!memo]
> Very interesting example...
```

## 5. File Naming Convention

- **Format:** `<citation_key> <entry_type>-ab.<ext>`
- **Example:** `Harari2015-ab book-ab.md`
- **Requirement:** A matching BibTeX entry is mandatory. If no entry is found for a book, a warning will be logged, and no files will be created for that book.