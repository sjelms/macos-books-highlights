#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import click
from pathlib import Path
from itertools import groupby
from operator import itemgetter

from apple_books_highlights import booksdb
from apple_books_highlights.bib import BibTexLibrarian
from apple_books_highlights.export_json import JsonExporter
from apple_books_highlights.export_md import MarkdownExporter
from apple_books_highlights.export_csv import CsvExporter

def load_config(config_path='config.yaml'):
    """Load shared defaults and any ignored local overrides."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    local_path = Path(config_path).with_name('config.local.yaml')
    if local_path.is_file():
        with local_path.open() as f:
            config.update(yaml.safe_load(f) or {})
    return config

@click.group()
def cli():
    """Apple Books Highlights Export Tool"""
    pass

@cli.command()
@click.option('--norefresh', '-n', default=False, is_flag=True, help="Disable refreshing the database by opening and closing Apple Books.")
def sync(norefresh):
    """Extracts highlights, enriches them with BibTeX, and exports to JSON, Markdown, and CSV."""
    
    # T017: Load config
    config = load_config()
    bibtex_path = config['bibtex_path']
    json_dir = config['json_output_dir']
    md_dir = config['md_output_dir']
    csv_dir = config['csv_output_dir']

    # Initialize exporters and librarian
    bib_librarian = BibTexLibrarian(bibtex_path)
    json_exporter = JsonExporter(json_dir)
    md_exporter = MarkdownExporter(md_dir)
    csv_exporter = CsvExporter(csv_dir)

    # T018: Fetch all annotations
    click.echo("Fetching annotations from Apple Books database...")
    all_annotations = booksdb.fetch_annotations(refresh=not norefresh)
    click.echo(f"Found {len(all_annotations)} total annotations.")

    # T019: Group annotations by book (asset_id)
    key = itemgetter('asset_id')
    grouped_annotations = {k: list(v) for k, v in groupby(sorted(all_annotations, key=key), key=key)}
    click.echo(f"Annotations are from {len(grouped_annotations)} different books.")

    # --- Main Processing Loop ---
    # T020 & T021: Process each book
    for asset_id, annotations in grouped_annotations.items():
        book_title = annotations[0]['title']
        book_author = annotations[0]['author']
        
        click.echo(f"\nProcessing: {book_title} by {book_author}")

        # 1. Enrich with BibTeX and create JSON
        enriched_json_path = json_exporter.export(annotations, bib_librarian)

        if not enriched_json_path:
            click.echo(f"  ✗ Skipped (no BibTeX match found).")
            continue
        
        click.echo(f"  ✓ Enriched JSON created.")

        # 2. Export to Markdown (Append-Only)
        md_exporter.export(enriched_json_path)
        click.echo(f"  ✓ Markdown export complete.")

        # 3. Export to CSV
        csv_exporter.export(enriched_json_path)
        click.echo(f"  ✓ CSV export complete.")

    click.echo("\nSync complete!")

if __name__ == '__main__':
    cli()
