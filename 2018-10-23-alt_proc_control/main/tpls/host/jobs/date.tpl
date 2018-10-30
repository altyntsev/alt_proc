{% extends "host/jobs/menu.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-date';</script>
{% endblock %}

{% block content %}
<form data-autosubmit>
    <div id="date" style="display: inline-block;">
        <div class="input-group dp-group">
            <span class="input-group-label igbutton dp-left"><i class="fa fa-caret-left"></i></span>
            <input type="text" class="form-control" name="date" id="date" data-select="datepicker">
            <span class="input-group-label igbutton dp-right"><i class="fa fa-caret-right"></i></span>
            <span class="input-group-label igbutton dp-btn" data-toggle="datepicker"><i class="fa fa-calendar"></i></span>
            <span class="input-group-label igbutton dp-today"><i class="fa fa-calendar-check-o"></i></span>
        </div>
    </div>
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
    <span>Total: {{jobs|length}}</span>
</form>

{% include "host/jobs/table.tpl" %}

{% endblock %}
