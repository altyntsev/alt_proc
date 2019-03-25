{% extends "main.tpl" %}
{% block head %}
    <script>$$.menu_id='.menu-jobs';</script>
    <style>
        table {
            display: inline;
            margin: 1em;
        }
    </style>
{% endblock %}
{% block content %}
<div style="margin: .5rem;">

<h1>Job: {{ job.job_id }} / {{ task.name }}
    {% if task.type!='PERIODIC' %}/ {{ event.param }}{% endif %}
</h1>

<div style="margin: .5rem;">
    <input type="button" value="Delete"
            onclick="send_cmd('DEL_JOB', {job_id:'{{ job.job_id }}'})" />
    <input type="button" value="ReRun"
            onclick="send_cmd('RERUN_JOB', {job_id:'{{ job.job_id }}'})" />
    <input type="button" value="Delete And Remit Event"
            onclick="send_cmd('DEL_AND REEMIT', {job_id:'{{ job.job_id }}'})" />
    {%  if job.status=='WAIT' %}
        <input type="button" value="Run Now"
                onclick="send_cmd('RUN_JOB_NOW', {job_id:'{{ job.job_id }}'})" />
    {% endif %}
</div>

<table style="border: none;"><tr>

<td style="border: none;">
<table style="display: block;">
    <tr><th colspan="2">Task</th></tr>
    <tr><th>Name</th><td class="{{ task.status }}">{{ task.name }}</td></tr>
    <tr><th>Status</th><td class="{{ task.status }}">{{ task.status }}</td></tr>
</table>

{% if task.type!='PERIODIC' %}
    <table>
        <tr><th colspan="2">Event</th></tr>
        <tr><th>param</th><td>{{ event.param }}</td></tr>
        <tr><th>params</th><td>{{ event.params if event.params!=None }}</td></tr>
    </table>
{% endif %}

<table style="display: block;">
    <tr><th colspan="2">Job</th></tr>
    <tr><th>ID</th><td>{{ job.job_id }}</td></tr>
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
    <tr><th>mtime</th><td>{{ job.mtime_diff }}</td></tr>
    <tr><th>ctime</th><td>{{ job.ctime_diff }}</td></tr>
    <tr><th>wtime</th><td>
        {% if job.stime and job.etime %}
            {{ job.stime_diff }}-{{ job.etime_diff }}={{ job.wtime }}
        {% else %}
            {{ job.stime_diff }}
        {% endif %}
    </td></tr>
    <tr><th>run_at</th><td>{{ job.run_at_diff }}</td></tr>
</table>
</td>

<td style="border: none;">
<table style="display: block;">
    <tr><th colspan="100">Scripts</th></tr>
    <tr>
        <th>i</th><th>name</th><th>cmd</th><th>status</th><th>result</th>
        <th>wtime</th><th>Control</th>
    </tr>
    {% for script in scripts %}
        <tr>
            <th>{{ script.iscript }}</th>
            <th>{{ script.name }}</th>
            <td>{{ script.cmd }}</td>
            <td class="{{ script.status }}">{{ script.status }}</td>
            <td class="{{ script.result }}">{{ script.result if script.result!=None }}</td>
            <td>
                {% if script.stime and script.etime %}
                    {{ script.stime_diff }}-{{ script.etime_diff }}={{ script.wtime }}
                {% else %}
                    {{ script.stime_diff }}
                {% endif %}
            </td>
            <td>
                <input type="button" value="ReRun"
                    onclick="send_cmd('RERUN_SCRIPT', {script_id:'{{ script.script_id }}'})" />
            </td>
        </tr>
    {% endfor %}

</table>
</td>

</tr></table>

</div>

{% endblock %}