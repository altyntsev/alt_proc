{% extends "hub/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-hosts';</script>
{% endblock %}
{% block content %}
    <form method="post">
        <div class="grid-x grid-padding-x" style="width: 30rem;">
            <h1>
                Host {% if host_id=='new' %} New {% else %} {{ host.name }} {% endif %}
            </h1>
            <div class="cell">
                <label>Host Name</label>
                <input type="text" name="name">
            </div>
            <div class="cell">
                <label>Time Zone</label>
                <input type="text" name="tz" placeholder="0">
            </div>
            <div class="cell">
                <input type="submit" value="Save" />
            </div>
        </div>
    </form>
{% endblock %}