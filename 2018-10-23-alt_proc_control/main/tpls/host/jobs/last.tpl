{% extends "host/jobs/menu.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-last';</script>
{% endblock %}

{% block content %}
<form data-autosubmit>
    <select name="task">
        <option value="">All</option>
        <option value="_periodic">periodic</option>
        {% for task in tasks %}
            <option value="{{task.name}}">{{task.name}}</option>
        {% endfor %}
    </select>
    <select name="result">
        <option value="">All</option>
        <option value="fatal">Fatal</option>
    </select>
    <select name="limit">
        <option value="30">30</option>
        <option value="100">100</option>
        <option value="500">500</option>
    </select>
    <span>Total: {{jobs|length}}</span>
</form>

{% include "host/jobs/table.tpl" %}

{% endblock %}
