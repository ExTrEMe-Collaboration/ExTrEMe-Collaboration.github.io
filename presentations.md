---
layout: page
title: Presentations and Talks
permalink: /presentations/
---

Invited talks, conference presentations, and seminars given by members of the ExTrEMe Collaboration.

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
