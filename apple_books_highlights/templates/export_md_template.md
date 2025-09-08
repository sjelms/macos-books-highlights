---
title: "{{ metadata.title }}"
year: {{ metadata.year }}
{% for author in metadata.authors %}author-{{ loop.index }}: "[[{{ author }}]]"
{% endfor %}
citation-key: "[[@{{ metadata.citation_key }}]]"
book-id: {{ metadata.asset_id }}
highlights: {{ annotations|length }}
creation: {{ creation_date }}
modified: {{ modified_date }}
type: "#{{ metadata.entry_type }}-ab"
aliases:
  - "{{ metadata.title }}"
{% if metadata.short_title and metadata.short_title != metadata.title %}  - "{{ metadata.short_title }}"
{% endif %}
---

## Highlights for [[@{{ metadata.citation_key }}]] on [[@{{ metadata.citation_key }}|{{ creation_date_short }}]]
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

