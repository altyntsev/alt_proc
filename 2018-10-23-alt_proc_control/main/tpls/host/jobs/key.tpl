{% extends "host/jobs/menu.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-key';</script>
{% endblock %}

{% block content %}
<form data-autosubmit>
    <input placeholder="Key" type="text" id="key" name="key" style="width: 30rem;">
</form>

{% include "host/jobs/table.tpl" %}

{% endblock %}
