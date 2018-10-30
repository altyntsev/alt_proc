{% extends "host/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-tasks';</script>
{% endblock %}
{% block content %}

    <a href="{{_root}}/config/task/edit/new/?type=periodic">
        <input type="button" value="New Periodic Task"/></a>
    <a href="{{_root}}/config/task/edit/new/?type=EVENT">
        <input type="button" value="New Regular Task"/></a>
    <table>
        <thead><tr>
            <th>Project</th>
            <th>Name</th>
            <th>Type</th>
            <th>Job</th>
            <th>Status</th>
            <th>Edit</th>
        </tr></thead>
        {% for task in tasks %}
            <tr>
                <td>{{task.project}}</td>
                <td>{{task.name}}</td>
                <td>{{task.type}}</td>
                <td>{{task.job}}</td>
                <td class="{{ task.status }}">{{ task.status }}</td>
                <td>
                    <a href="{{_root}}/config/task/edit/{{ task.id }}/">
                        <input type="button" value="Edit"/></a>
                </td>
            </tr>
        {% endfor %}
    </table>

{% endblock %}