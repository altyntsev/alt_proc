{% extends "host/jobs/menu.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-param';</script>
{% endblock %}

{% block content %}
<form data-autosubmit>
    <input placeholder="param" type="text" id="param" name="param" style="width: 30rem;">
</form>

{% include "host/jobs/table.tpl" %}

{% endblock %}
