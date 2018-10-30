{% extends 'main.tpl' %}

{% block head %}
    <script>$$.menu_id='.menu-config';</script>
{% endblock %}

{% block submenu %}

    <div class="tab-list">
        <span class="tab-line"></span>
        <a class="tab submenu-tasks" href="{{_root}}/config/tasks/">Tasks</a>
        <a class="tab submenu-msgs" href="{{_root}}/config/msgs/">Messages</a>
        <span class="tab-line"></span>
    </div>

{% endblock %}