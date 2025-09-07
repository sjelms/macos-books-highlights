---
title: "{{ metadata.title }}"
year: {{ metadata.year }}
{% for author in metadata.authors %}author-{{ loop.index }}: "[[{{ author }}]]"
{% endfor %}
citation-key: "[[@{{ metadata.citation_key }}]]"
highlights: {{ annotations|length }}
type: "#{{ metadata.entry_type }}-ab"
aliases:
  - "{{ metadata.title }}"
{% if metadata.short_title and metadata.short_title != metadata.title %}  - "{{ metadata.short_title }}"
{% endif %}
---

# Highlights for [[@{{ metadata.citation_key }}]]

{% for annotation in annotations %}
- {{ annotation.highlight }}
> chapter: `{{ annotation.chapter }}`
> tags: {{ annotation.tag | default('#general-ab') }}
{% if annotation.note %}

>[!memo]
> {{ annotation.note }}
{% endif %}
{% endfor %}
