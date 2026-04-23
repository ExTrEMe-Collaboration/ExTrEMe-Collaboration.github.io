---
layout: page
title: Presentations and Talks
permalink: /presentations/
---

This page is rendered from `/_data/talks.yml`.

{% assign talks_sorted = site.data.talks | sort: "date_sort" | reverse %}
{% assign current_year = "" %}

{% for item in talks_sorted %}
{% unless item.year == current_year %}
## {{ item.year }}
{% assign current_year = item.year %}
{% endunless %}

- **{{ item.month }}** - {{ item.speaker }} - {{ item.type }} - {{ item.event }}
  
  {{ item.title }}{% if item.location %} ({{ item.location }}){% endif %}{% if item.url %} - [Link]({{ item.url }}){% endif %}
{% endfor %}

## Legacy Source

- [Legacy homepage presentation list](https://sites.ifi.unicamp.br/extreme/)

## Maintenance

- Add or update entries in `/_data/talks.yml`
- Keep `date_sort` in `YYYY-MM` format for ordering
