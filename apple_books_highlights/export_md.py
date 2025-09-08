"""
Handles the creation and updating of the Markdown export file.
"""
import json
import pathlib
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

# As per TECHNICAL.md, this is the required timestamp format for Obsidian.
OBSIDIAN_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# Mapping of Apple Books highlight color IDs to tags.
# Based on common observation: 0: Yellow, 1: Green, 2: Blue, 3: Pink, 4: Purple
# The original `style` field from the DB is the key.
COLOR_MAP = {
    0: '#general-ab',      # Yellow
    1: '#important-ab',      # Green
    2: '#reference-note-ab', # Blue
    3: '#secondary-ab',      # Pink
    4: '#review-ab'          # Purple
}

# This is the template for appending NEW highlights to an existing file.
APPEND_TEMPLATE = """ 

### New highlights added on [[@{{ metadata.citation_key }}|{{ date_short }}]]
{% for annotation in annotations %}
<!-- an_id: {{ annotation.annotation_id }} -->
- {{ annotation.highlight }}
{% if annotation.location %}> page: `{{ annotation.location }}`
{% endif %}{% if annotation.chapter %}> chapter:  `{{ annotation.chapter }}`
{% endif %}> tags: {{ annotation.tag | default('#general-ab') }}
{% if annotation.note %}

>[!memo]
> {{ annotation.note }}
{% endif %}{% endfor %}
"""

class MarkdownExporter:
    """Orchestrates the creation and append-only updating of Markdown files."""

    def __init__(self, output_dir: str):
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        template_dir = pathlib.Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
        self.main_template = self.jinja_env.get_template('export_md_template.md')
        self.append_template = Template(APPEND_TEMPLATE)

    def _add_tags_to_annotations(self, annotations):
        """Adds a 'tag' field to each annotation based on its color code."""
        for ann in annotations:
            ann['tag'] = COLOR_MAP.get(ann.get('color'), '#general-ab')
        return annotations

    def export(self, enriched_json_path: str):
        """Creates or updates a Markdown file from an enriched JSON file."""
        with open(enriched_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data['metadata']
        annotations = self._add_tags_to_annotations(data['annotations'])

        filename = f"{metadata['citation_key']} {metadata['entry_type']}-ab.md"
        md_path = self.output_dir / filename

        now = datetime.now()
        now_str = now.strftime(OBSIDIAN_TIMESTAMP_FORMAT)

        if not md_path.exists():
            # --- Create new file ---
            render_context = {
                "metadata": metadata,
                "annotations": annotations,
                "creation_date": now_str,
                "modified_date": now_str,
                "creation_date_short": now.strftime('%Y-%m-%d')
            }
            markdown_content = self.main_template.render(render_context)
            md_path.write_text(markdown_content, encoding='utf-8')
        else:
            # --- Update existing file ---
            content = md_path.read_text(encoding='utf-8')
            existing_ids = set(re.findall(r"<!-- an_id: (.*?) -->", content))
            
            new_annotations = [ann for ann in annotations if ann['annotation_id'] not in existing_ids]

            if not new_annotations:
                return # No new highlights to add

            # Append new highlights to the file
            append_context = {
                "metadata": metadata,
                "annotations": new_annotations,
                "date_short": now.strftime('%Y-%m-%d')
            }
            append_content = self.append_template.render(append_context)
            with md_path.open('a', encoding='utf-8') as f:
                f.write(append_content)

            # Update the 'modified' timestamp in the YAML front matter
            # Use a lambda to ensure the replacement is handled correctly
            new_content = re.sub(r"^(modified: ).*$", lambda m: m.group(1) + now_str, content, flags=re.MULTILINE)
            md_path.write_text(new_content, encoding='utf-8')
