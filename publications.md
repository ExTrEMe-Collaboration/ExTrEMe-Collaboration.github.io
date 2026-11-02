---
layout: page
title: Publications
permalink: /publications/
---

Research articles, conference proceedings, preprints, and academic theses produced by members and affiliates of the ExTrEMe Collaboration.

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
