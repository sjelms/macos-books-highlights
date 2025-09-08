# Tasks: Merging Apple Books and PDF Highlight Workflows

**Objective**: Refactor the `apple-books-highlights` project to incorporate the BibTeX enrichment and structured export workflow from the `pdf-highlight-extraction` project, using its file naming conventions.

Python and packages `~/python-venv/`

---

## Phase 1: Setup & Scaffolding

- [x] T001 [P] Create new file `apple_books_highlights/bib.py` for all BibTeX processing logic.
- [x] T002 [P] Create new file `apple_books_highlights/export_json.py` for creating the enriched JSON files.
- [x] T003 [P] Create new file `apple_books_highlights/export_md.py` for Markdown export logic.
- [x] T004 [P] Create new file `apple_books_highlights/export_csv.py` for CSV export logic.
- [x] T005 [P] Create new file `apple_books_highlights/ui_notifications.py` for user-facing dialogs.
- [x] T006 [P] Create `config.yaml` in the root directory to manage paths for the BibTeX library and output directories.
- [x] T007 Consolidate dependencies from `setup.py` and `_reference_project/requirements.txt` into a single, unified `requirements.txt` file. Key dependencies: `bibtexparser`, `thefuzz[speedup]`, `PyYAML`, `Jinja2`, `pydantic`.
- [x] T008 Update `setup.py` to reflect the new dependencies and project structure.
- [x] T008a Confirm all required dependencies (bibtexparser, thefuzz, PyYAML, Jinja2, pydantic) are installed and up-to-date.

## Phase 2: Core Logic Implementation

- [x] T009 Adapt all BibTeX processing code from `_reference_project/bib.py` into `apple_books_highlights/bib.py`. This includes `load_bibtex`, `find_bibtex_entry`, and the critical `normalize_meta` function.
- [x] T010 Modify the `find_bibtex_entry` function in `apple_books_highlights/bib.py` to accept book title and author strings from Apple Books data instead of a PDF filename.
- [x] T011 Implement the main logic in `apple_books_highlights/export_json.py`. This module will:
    - Define the Pydantic models for `Annotation`, `Metadata`, and `EnrichedJSON`.
    - Import from `booksdb` and `bib`.
    - Contain the primary function to take raw book data, call `bib.py` to get enriched metadata, construct the `EnrichedJSON` object, and save it to a file.
    - Handle cases where no BibTeX match is found by logging a warning.
- [x] T012 Update the Jinja2 template at `apple_books_highlights/templates/export_md_template.md` to match the exact YAML and body format required by `TECHNICAL.md` for initial file creation.
- [x] T013 Implement the append-only `create_markdown_export` in `apple_books_highlights/export_md.py`. This function will orchestrate the entire Markdown creation and update process.
- [x] T013a In `export_md.py`, implement logic to read existing Markdown files and parse them to extract the unique IDs of all highlights already present (e.g., from HTML comments).
- [x] T013b In `export_md.py`, implement the core append/update logic: if a file exists, determine new highlights, append them under a "New highlights added on..." heading, and update the `modified` timestamp. If it doesn't exist, create it from the template.
- [x] T014 Implement `create_readwise_csv` in `apple_books_highlights/export_csv.py` to generate a CSV file from an enriched JSON file.
- [x] T014a Modify `booksdb.py` to extract a unique identifier (e.g., `ZANNOTATIONUUID`) for each annotation and include it in the returned data.
- [x] T014b Populate `config.yaml` with default paths for bibtex_path and output directories.

## Phase 3: Integration & Workflow Orchestration

- [x] T015 Refactor the main script `scripts/apple-books-highlights.py` to orchestrate the new workflow, mirroring `_reference_project/pdf-highlight-extraction.py`.
- [x] T016 In `scripts/apple-books-highlights.py`, remove the old direct-to-markdown logic.
- [x] T017 In `scripts/apple-books-highlights.py`, add logic to load the `config.yaml`.
- [x] T018 In `scripts/apple-books-highlights.py`, call `booksdb.fetch_annotations()` to get all raw highlight data.
- [x] T019 In `scripts/apple-books-highlights.py`, group the raw annotations by book.
- [x] T020 For each book, call the function from `export_json.py` to create and save the enriched JSON file to the directory specified in `config.yaml`.
- [x] T021 For each successfully created JSON file, call the `create_markdown_export` (now an append/update operation) and `create_readwise_csv` functions.
- [ ] T022 Add robust logging throughout the main script to report progress, warnings (e.g., no BibTeX match), and errors.
- [ ] T023 Adapt `ui_notifications.py` to show a summary dialog, and integrate the call into the main script in `scripts/apple-books-highlights.py`.

## Phase 4: Testing and Polish

- [ ] T024 Investigate Apple Books database to identify the actual values for highlight colors (e.g., 'Yellow', 'Blue') and update the `color_map` in `apple_books_highlights/export_md.py`.
- [ ] T025 [P] Create `tests/test_bib.py` and write unit tests for the `normalize_meta` function.
- [ ] T026 [P] Create `tests/test_export_md.py` and write unit tests to ensure the Markdown output is formatted correctly for both initial creation and for subsequent appends.
- [ ] T027 Create an integration test in `tests/test_workflow.py` that uses a sample `paperpile.bib` and mocked data from `booksdb` to test the entire pipeline.
- [ ] T028 Review all new and modified files for code quality, comments, and docstrings.
- [ ] T029 Manually run the script and verify the output files in a text editor and Obsidian to confirm perfect formatting, especially the append-only behavior.

---
## Dependencies

- **Phase 1** must be complete before **Phase 2**.
- **T009 (bib.py)** and **T011 (export_json.py)** are prerequisites for the rest of Phase 2 and 3.
- **Phase 2** must be complete before **Phase 3**.
- **Phase 3** must be complete before **Phase 4**.