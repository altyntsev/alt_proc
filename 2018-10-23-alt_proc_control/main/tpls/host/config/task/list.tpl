{% extends "host/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-tasks';</script>
{% endblock %}
{% block content %}
    {% if 'admin' in _roles %}
        <a href="{{_root}}/host/config/task/edit/new/?type=periodic">
            <input type="button" value="New Periodic Task"/></a>
        <a href="{{_root}}/host/config/task/edit/new/?type=event">
            <input type="button" value="New Event Task"/></a>
    {% endif %}
    <table>
        <thead><tr>
            <th>status</th>
            <th>project</th>
            <th>name</th>
            <th>type</th>
            <th>priority</th>
            <th>period</th>
            <th>n_runs</th>
            <th>n_fatals</th>
            {% if 'admin' in _roles %}
                <th>Controls</th>
            {% endif %}
        </tr></thead>
        {% for task in tasks %}
            <tr>
                <td class="{{ task.status }}">{{ task.status }}</td>
                <td>{{task.project}}</td>
                <td>{{task.name}}</td>
                <td>{{task.type}}</td>
                <td>{{task.priority}}</td>
                <td>{{task.period if task.period!=None}}</td>
                <td>{{task.n_runs}}</td>
                <td>{{task.n_fatals if task.n_fatals!=0 else 'No'}}</td>
                {% if 'admin' in _roles %}
                    <td>
                        <a href="{{_root}}/host/config/task/edit/{{ task.task_id }}/">
                            <input type="button" value="Edit"/></a>
                        <a onclick="send_cmd('SET_TASK_STATUS',
                                {task_id: '{{ task.task_id }}', status: 'DELETED'})">
                            <input type="button" value="Del"/></a>
                    </td>
                {% endif %}
            </tr>
        {% endfor %}
    </table>

{% endblock %}