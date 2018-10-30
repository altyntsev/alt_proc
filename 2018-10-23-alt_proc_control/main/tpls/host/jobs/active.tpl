{% extends "host/jobs/menu.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-active';</script>
{% endblock %}

{% block content %}

{% include "host/jobs/table.tpl" %}

{% endblock %}
