{% extends "host/config/menu.tpl" %}
{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.submenu-msgs';</script>
{% endblock %}
{% block content %}
    {% if 'admin' in _roles %}
        <form method="post">
            todo task script msg delay
            <textarea name="text" rows="20"
                      style="font-size: large; font-family: monospace;">
            </textarea>
                <input type="submit" value="Send">
        </form>
    {% else %}
        {{ _form.text }}
    {% endif %}
{% endblock %}