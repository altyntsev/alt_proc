{% extends "main.tpl" %}
{% block head %}
    <script>$$.menu_id='.menu-jobs';</script>
{% endblock %}
{% block content %}
<div style="margin: .5rem;">

<h1>Job: {{ task.name }}
    {% if task.type!='PERIODIC' %}/ {{ event.param }}{% endif %}
</h1>

<div style="margin: .5rem;">
    <input type="button" value="Delete"
            onclick="send_cmd('DEL_JOB', {job_id:'{{ job.id }}'})" />
    <input type="button" value="ReRun"
            onclick="send_cmd('RERUN_JOB', {job_id:'{{ job.id }}'})" />
    {%  if job.status=='WAIT' %}
        <input type="button" value="Run Now"
                onclick="send_cmd('RUN_JOB_NOW', {job_id:'{{ job.id }}'})" />
    {% endif %}
</div>

<table>
    <tr><th colspan="2">Task</th></tr>
    <tr><th>Name</th><td class="{{ task.status }}">{{ task.name }}</td></tr>
    <tr><th>Status</th><td class="{{ task.status }}">{{ task.status }}</td></tr>
</table>

{% if task.type!='PERIODIC' %}
    <table>
        <tr><th colspan="2">Event</th></tr>
        <tr><th>param</th><td>{{ event.param }}</td></tr>
    </table>
{% endif %}

<table>
    <tr><th colspan="2">Job</th></tr>
    <tr><th>ID</th><td>{{ job.id }}</td></tr>
    <tr><th>Status</th><td class="{{ job.status }}">{{ job.status }}</td></tr>
    <tr><th>Result</th><td class="{{ job.result }}">{{ job.result }}</td></tr>
    <tr><th>ToDo</th>
        {% if job.todo %}
            <td>
                <span  class="TODO">TODO</span>
            </td>
        {% else %}
            <td></td>
        {% endif %}
    </tr>
    <tr><td>ctime</td><td>{{ job.ctime }}</td></tr>
    <tr><td>stime</td><td>{{ job.stime }}</td></tr>
    <tr><td>etime</td><td>{{ job.etime }}</td></tr>
    <tr><td>mtime</td><td>{{ job.mtime }}</td></tr>
    <tr><td>run_at</td><td>{{ job.run_at }}</td></tr>
</table>

<table>
    <tr><th colspan="5">Scripts</th></tr>
    {% for script in scripts %}
        <tr>
            <th>{{ script.iscript }}</th>
            <th>{{ script.name }}</th>
            <td>{{ script.cmd }}</td>
            <td class="{{ script.status }}">{{ script.status }}</td>
            <td class="{{ script.result }}">{{ script.result }}</td>
            <td>{{ script.stime }}</td>
            <td>{{ script.etime }}</td>
            <td>{{ script.msgs }}</td>
            <td>{{ script.restart_after }}</td>
        </tr>
    {% endfor %}

</table>

</div>

{% endblock %}