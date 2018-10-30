{% extends "main.tpl" %}
{% block head %}
    <script>$$.menu_id='.menu-status';</script>
{% endblock %}
{% block content %}
    <table>
        <thead><tr>
            {% include 'host/status_header.tpl' %}
        </tr></thead>
        {% for host in hosts_ %}
            <tr>
                <td style="background-color: yellow;">
                    <a href="{{ root }}/{{ host.name }}/status/">
                        <b>{{ host.name }}</b></a>
                    <span class="{{ host.status }}">{{ host.status }}</span>
                    {% if host.manager_mtime[:-2]!='(00:0' %}
                        <span class="TODO">{{ host.manager_mtime }}</span>
                    {% endif %}
                    {% if host.repl_status %}
                        <span class="{{ host.repl_status }}">R</span>
                    {% endif %}
                </td>
            <tr>
            {% for task in host.tasks %}
                <tr>
                    <td class="{{ task.status }}">
                        <span>{{task.name}}</span>
                    </td>
                    {% include 'host/status_table.tpl' %}
                </tr>
            {% endfor %}
        {% endfor %}
    </table>
{% endblock %}