{% extends "host/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-tasks';</script>
{% endblock %}
{% block content %}
    <form method="post">
        <input type="hidden" name="type" value="{{ task.type }}">
        <div class="grid-container">
        <h1>
            {% if task_id=='new' %} New Task {% else %} Task: {{task.name}} {% endif %}
            / {{ task.type }}
        </h1>
        <div class="grid-x grid-padding-x" style="max-width: 30rem;">
            <div class="cell">
                <label>Task Name</label>
                <input type="text" name="name" placeholder="Task Name">
            </div>
            <div class="cell">
                <label>Period</label>
                <select class="ui dropdown" name="period">
                    <option value=1>1 min</option>
                    <option value=5>5 min</option>
                    <option value=10>10 min</option>
                    <option value=60>1 Hour</option>
                    <option value=720>12 Hour</option>
                    <option value=1440>1 Day</option>
                </select>
            </div>
            <div class="cell">
                <label>Project</label>
                <input type="text" name="project" placeholder="YEAR-MM-DD-project">
            </div>
            <div class="cell">
                <label>Job</label>
                <input type="text" name="job" placeholder="doit">
            </div>
            <div class="cell">
                <label>Priority</label>
                <select class="ui dropdown" name="priority" id="priority">
                    <option value=0>Background</option>
                    <option value=1>Regular</option>
                    <option value=2>Operative</option>
                    <option value=3>High</option>
                    <option value=4>Urgent</option>
                </select>
            </div>
            <div class="cell" style="margin-top: 1rem;">
                <input type="submit" value="Save" />
            </div>
        </div>
        </div>
    </form>
<script>
</script>
{% endblock %}