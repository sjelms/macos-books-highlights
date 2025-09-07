# Tasks: Merging Apple Books and PDF Highlight Workflows

**Objective**: Refactor the `apple-books-highlights` project to incorporate the BibTeX enrichment and structured export workflow from the `pdf-highlight-extraction` project, using its file naming conventions.

---

## Phase 1: Setup & Scaffolding

- [ ] T001 [P] Create new file `apple_books_highlights/bib.py` for all BibTeX processing logic.
- [ ] T002 [P] Create new file `apple_books_highlights/export_json.py` for creating the enriched JSON files.
- [ ] T003 [P] Create new file `apple_books_highlights/export_md.py` for Markdown export logic.
- [ ] T004 [P] Create new file `apple_books_highlights/export_csv.py` for CSV export logic.
- [ ] T005 [P] Create new file `apple_books_highlights/ui_notifications.py` for user-facing dialogs.
- [ ] T006 [P] Create `config.yaml` in the root directory to manage paths for the BibTeX library and output directories.
- [ ] T007 Consolidate dependencies from `setup.py` and `_reference_project/requirements.txt` into a single, unified `requirements.txt` file. Key dependencies: `bibtexparser`, `thefuzz[speedup]`, `PyYAML`, `Jinja2`, `pydantic`.
- [ ] T008 Update `setup.py` to reflect the new dependencies and project structure.

## Phase 2: Core Logic Implementation

- [ ] T009 Adapt all BibTeX processing code from `_reference_project/bib.py` into `apple_books_highlights/bib.py`. This includes `load_bibtex`, `find_bibtex_entry`, and the critical `normalize_meta` function.
- [ ] T010 Modify the `find_bibtex_entry` function in `apple_books_highlights/bib.py` to accept book title and author strings from Apple Books data instead of a PDF filename.
- [ ] T011 Implement the main logic in `apple_books_highlights/export_json.py`. This module will:
    - Define the Pydantic models for `Annotation`, `Metadata`, and `EnrichedJSON`.
    - Import from `booksdb` and `bib`.
    - Contain the primary function to take raw book data, call `bib.py` to get enriched metadata, construct the `EnrichedJSON` object, and save it to a file.
    - Handle cases where no BibTeX match is found by logging a warning.
- [ ] T012 Update the Jinja2 template at `apple_books_highlights/templates/markdown_template.md` to match the exact YAML and body format required by `TECHNICAL.md`.
- [ ] T013 Implement `create_markdown_export` in `apple_books_highlights/export_md.py`. This function will take a path to an enriched JSON file, load it, and use the Jinja2 template to render the final Markdown file.
- [ ] T014 Implement `create_readwise_csv` in `apple_books_highlights/export_csv.py` to generate a CSV file from an enriched JSON file.

## Phase 3: Integration & Workflow Orchestration

- [ ] T015 Refactor the main script `scripts/apple-books-highlights.py` to orchestrate the new workflow, mirroring `_reference_project/pdf-highlight-extraction.py`.
- [ ] T016 In `scripts/apple-books-highlights.py`, remove the old direct-to-markdown logic.
- [ ] T017 In `scripts/apple-books-highlights.py`, add logic to load the `config.yaml`.
- [ ] T018 In `scripts/apple-books-highlights.py`, call `booksdb.fetch_annotations()` to get all raw highlight data.
- [ ] T019 In `scripts/apple-books-highlights.py`, group the raw annotations by book.
- [ ] T020 For each book, call the function from `export_json.py` to create and save the enriched JSON file to the directory specified in `config.yaml`.
- [ ] T021 For each successfully created JSON file, call the `create_markdown_export` and `create_readwise_csv` functions from their respective modules.
- [ ] T022 Add robust logging throughout the main script to report progress, warnings (e.g., no BibTeX match), and errors.
- [ ] T023 Adapt the code from `_reference_project/ui_notifications.py` into `apple_books_highlights/ui_notifications.py` to show a summary dialog upon completion.

## Phase 4: Testing and Polish

- [ ] T024 [P] Create `tests/test_bib.py` and write unit tests for the `normalize_meta` function.
- [ ] T025 [P] Create `tests/test_export_md.py` and write a unit test to ensure the Markdown output is formatted exactly as required.
- [ ] T026 Create an integration test in `tests/test_workflow.py` that uses a sample `paperpile.bib` and mocked data from `booksdb` to test the entire pipeline.
- [ ] T027 Review all new and modified files for code quality, comments, and docstrings.
- [ ] T028 Manually run the script and verify the output files in a text editor and Obsidian to confirm perfect formatting.

---
## Dependencies

- **Phase 1** must be complete before **Phase 2**.
- **T009 (bib.py)** and **T011 (export_json.py)** are prerequisites for the rest of Phase 2 and 3.
- **Phase 2** must be complete before **Phase 3**.
- **Phase 3** must be complete before **Phase 4**.