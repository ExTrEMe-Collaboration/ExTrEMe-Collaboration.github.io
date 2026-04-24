---
layout: page
title: Publications
permalink: /publications/
---

This page is rendered from `/_data/publications.yml`.

{% for group in site.data.publications %}
## {{ group.category }}

{% assign entries = group.items | sort: "year" | reverse %}
{% for paper in entries %}
- **{{ paper.year }}** - {{ paper.title }}
  
  Authors: {{ paper.authors }}
  
  Venue: {{ paper.venue }}
  
  {% if paper.doi %}[doi:{{ paper.doi }}](https://doi.org/{{ paper.doi }}){% endif %}{% if paper.arxiv %}{% if paper.doi %} \| {% endif %}[arXiv:{{ paper.arxiv }}](https://arxiv.org/abs/{{ paper.arxiv }}){% endif %}{% if paper.url %}{% if paper.doi or paper.arxiv %} \| {% endif %}[Repository]({{ paper.url }}){% endif %}
{% endfor %}

{% endfor %}

## Legacy Source

- [Legacy publications and theses page](https://sites.ifi.unicamp.br/hadrex/publicacoes/)

## Maintenance

- Add new entries by editing `/_data/publications.yml`
- `doi`: store just the DOI identifier (e.g., `10.1103/PhysRevC.102.064909`); URL is built automatically
- `arxiv`: store just the arXiv ID (e.g., `2311.02210`); URL is built automatically
- `url`: use for non-DOI links (e.g., thesis repositories)
