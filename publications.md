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
  
  {% if paper.doi %}DOI/Link: [{{ paper.doi }}]({{ paper.doi }}){% endif %}{% if paper.arxiv %}{% if paper.doi %} | {% endif %}arXiv: [{{ paper.arxiv }}]({{ paper.arxiv }}){% endif %}
{% endfor %}

{% endfor %}

## Legacy Source

- [Legacy publications and theses page](https://sites.ifi.unicamp.br/hadrex/publicacoes/)

## Maintenance

- Add new entries by editing `/_data/publications.yml`
- Keep links in DOI URL format when available
- Use the same schema for all categories
