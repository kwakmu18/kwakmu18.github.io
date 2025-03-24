---
title: "프로세스와 잡"
layout: archive
permalink: /categories/프로세스와-잡
author_profile: true
types: pages
---

{% assign posts = site.categories['프로세스와 잡']%}
{% for post in posts %}
  {% include archive-single.html type=page.entries_layout %}
{% endfor %}