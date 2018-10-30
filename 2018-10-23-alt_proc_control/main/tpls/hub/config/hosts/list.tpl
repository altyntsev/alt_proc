{% extends "hub/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-hosts';</script>
{% endblock %}
{% block content %}
    <a href="{{_root}}/config/host/edit/new/">
        <input type="button" value="Add Host">
    </a>
<table>
    <thead><tr><th>Name</th><th>TZ</th><th>Status</th></tr></thead>
    {% for host in host_list %}
        <tr>
            <td>{{host.name}}</td>
            <td>{{host.tz}}</td>
            <td class="{{ host.status }}">{{host.status}}</td>
        </tr>
    {% endfor %}
</table>

{% endblock %}