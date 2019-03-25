{% extends "host/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-resources';</script>
{% endblock %}
{% block content %}
    {% if 'admin' in _roles %}
        <form method="post">
            json
            <textarea name="text" rows="20"
                      style="font-size: large; font-family: monospace;">
            </textarea>
            <input type="submit" value="Send">
        </form>
    {% else %}
        {{ _form }}
    {% endif %}
{% endblock %}