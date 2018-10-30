{% extends "main.tpl" %}
{% block head %}
    <script>$$.menu_id='.menu-msgs';</script>
{% endblock %}
{% block content %}
<form data-autosubmit>
    <select name="task">
        <option value="">All</option>
        {% for task in tasks %}
            <option value="{{task.name}}">{{task.name}}</option>
        {% endfor %}
    </select>
    <select name="new">
        <option value="all">All</option>
        <option value="new">New</option>
    </select>
    <select name="limit">
        <option value="30">30</option>
        <option value="100">100</option>
        <option value="500">500</option>
    </select>
    <span>Total: {{msgs|length}}</span>
    {% if msgs %}
        <input type="button" value="Read All" onclick="msg_read({{ msg_ids }})" />
    {% endif %}
</form>
<table>
    <thead>
        <th>mtime</th><th>time</th><th>job_id</th><th>type</th>
        <th>msg</th><th>task</th><th>key</th><th>script</th><th>read</th>
    </thead>
    {% for msg in msgs %}
        <tr {% if not msg.active %}style="background-color: lightgrey;"{% endif %}>
            <td>{{msg.mtime}}</td>
            <td>{{msg.stime}} - {{msg.etime}} / {{ msg.diff }} {{ msg.n_runs }}</td>
            <td>{{msg.job_id}}</td>
            {% if msg.todo %}
                <td class="TODO">{{msg.type}}</td>
            {% else %}
                <td class="{{ msg.type }}">{{msg.type}}</td>
            {% endif %}
            <td>{{msg.msg}}</td>
            <td>{{msg.name}}</td>
            <td>{{msg.key}}</td>
            <td>{{msg.cmd}}</td>
            <td>
                {% if not msg.read %}
                    <input type="button" value="OK" onclick="msg_read([{{ msg.id }}])" />
                {% endif %}
            </td>
        </tr>
    {% endfor %}
</table>

{% endblock %}