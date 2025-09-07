"""
Handles the creation of the Markdown export file.
"""
import json
import os
from jinja2 import Environment, FileSystemLoader

def create_markdown_export(json_path: str, md_path: str):
    """
    Creates a Markdown export file from an enriched JSON file.

    Args:
        json_path: The path to the enriched JSON file.
        md_path: The path to save the Markdown file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)

    annotations = enriched_data.get("annotations", [])
    if not annotations:
        print(f"No annotations found in {json_path}. Skipping Markdown export.")
        return

    # Simple color to tag mapping (can be expanded in config)
    # Placeholder HEX colors for Apple Books. We will need to identify these.
    color_map = {
        '#FFD700': '#general-ab',      # Yellow
        '#ADD8E6': '#reference-note-ab', # Blue
        '#90EE90': '#important-ab',      # Green
        '#FFB6C1': '#secondary-ab',      # Pink
        '#E6E6FA': '#review-ab'          # Purple
    }

    # Add the appropriate tag to each annotation based on its color
    for annot in annotations:
        color = annot.get('color') # In Apple Books, this is just a word e.g. 'Yellow'
        # This is a placeholder. The actual color values will need to be determined.
        # For now, we will default all to #general-ab
        annot['tag'] = color_map.get(color, '#general-ab')

    # Set up Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('export_md_template.md')

    # Render the template with the data
    markdown_content = template.render(enriched_data)

    # Write to Markdown file
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Successfully created Markdown export at {md_path}")