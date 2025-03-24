---
title: "시스템 아키텍처"
layout: archive
permalink: /categories/시스템-아키텍처
author_profile: true
types: pages
---

{% assign posts = site.categories['시스템 아키텍처']%}
{% for post in posts %}
  {% include archive-single.html type=page.entries_layout %}
{% endfor %}