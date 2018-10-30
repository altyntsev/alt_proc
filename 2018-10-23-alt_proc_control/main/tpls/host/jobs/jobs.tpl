{% extends "host/jobs/menu.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-last';</script>
{% endblock %}

{% block content %}
<form data-autocommit>
    <select name="mode">
        <option value="last">Last</option>
        <option value="active">Active</option>
        <option value="date">Date</option>
        <option value="key">Key</option>
    </select>
    <div id="date" style="display: inline-block;">
        <div class="input-group dp-group">
            <span class="input-group-label igbutton dp-left"><i class="fa fa-caret-left"></i></span>
            <input type="text" class="form-control" name="date" id="date" data-select="datepicker">
            <span class="input-group-label igbutton dp-right"><i class="fa fa-caret-right"></i></span>
            <span class="input-group-label igbutton dp-btn" data-toggle="datepicker"><i class="fa fa-calendar"></i></span>
            <span class="input-group-label igbutton dp-today"><i class="fa fa-calendar-check-o"></i></span>
        </div>
    </div>

    {% if mode == 'last' or mode == 'date' %}
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
    {% endif %}
    {% if mode == 'key' %}
        <input placeholder="Key" type="text" id="key" name="key">
    {% endif %}
    <span class="large-1 cell">Total: {{jobs|length}}</span>
</form>

<table>
    <thead><tr>
        <th>id</th><th>mtime</th><th>task</th><th>key</th><th>status</th><th>result</th>
        <th>scripts</th><th>wtime</th><th>messages</th>
    </tr></thead>
    {% for job in jobs %}
        <tr>
            <td>{{job.id}}</td>
            <td>{{job.mtime}}</td>
            <td>{{job.task}}</td>
            {% if job.type=='PERIODIC' %}
                <td class="tac"><i class="fa fa-hourglass"></i></td>
            {% else %}
                <td class="tac">{{job.key}}</td>
            {% endif %}

            {% if not job.result %}
                <td class="{{job.status}} tac" colspan="2">{{job.status}}</td>
            {% elif job.status=='DONE' %}
                {% if job.todo %}
                    <td class="TODO tac" colspan="2">{{job.result}}</td>
                {% else %}
                    <td class="{{job.result}} tac" colspan="2">{{job.result}}</td>
                {% endif %}
            {% else %}
                <td class="{{job.status}} tac">{{job.status}}</td>
                {% if job.todo %}
                    <td class="TODO tac">{{job.result}}</td>
                {% else %}
                    <td class="{{job.result}} tac">{{job.result}}</td>
                {% endif %}
            {% endif %}

            <td>
                {% for script in job.scripts %}
                    <a href="{{ root }}/job/{{job.id}}/">
                        <span class="{{script.status}}_{{script.result}} script">{{script.name}}</span>
                    </a>
                {% endfor %}
            </td>
            <td>{{job.wtime if job.wtime!=None}}</td>
            <td>
                {% for msg in job.msgs %}
                    {% if msg.n_runs>1 %}
                        {{msg.n_runs}} {{msg.stime_diff}}
                    {% endif %}
                    {{msg.msg}}
                {% endfor %}
            </td>
        </tr>
    {% endfor %}
</table>

{% endblock %}
