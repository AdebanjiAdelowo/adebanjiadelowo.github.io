---
layout: page
title: Writing
permalink: /writing/
---

Technical notes, reproducibility reports, and tutorials on applied mathematics, scientific computing, and machine learning.

## Technical reports

- [Selected Projects Scientific Audit](https://github.com/AdebanjiAdelowo/selected-projects-scientific-audit) — project validation, experimental status, and limitations.

## Blog posts

{% for post in site.posts %}
- [{{ post.title }}]({{ post.url | relative_url }}) — {{ post.date | date: "%B %d, %Y" }}
{% else %}
New articles will appear here.
{% endfor %}
