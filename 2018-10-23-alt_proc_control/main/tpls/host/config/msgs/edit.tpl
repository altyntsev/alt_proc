{% extends "host/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-msgs';</script>
{% endblock %}
{% block content %}
    <form method="post">
        todo task script msg delay
        <textarea name="text" rows="20"
                  style="font-size: large; font-family: monospace;">
        </textarea>
        <input type="submit" value="Send">
    </form>
{% endblock %}