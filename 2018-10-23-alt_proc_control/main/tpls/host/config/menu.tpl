{% extends 'main.tpl' %}

{% block head %}
    <script>$$.menu_id='.menu-config';</script>
{% endblock %}

{% block submenu %}

    <div class="tab-list">
        <span class="tab-line"></span>
        <a class="tab submenu-tasks" href="{{_root}}/host/config/task/list/">Tasks</a>
        <a class="tab submenu-msgs" href="{{_root}}/host/config/msgs/edit/">Messages</a>
        <a class="tab submenu-resources" href="{{_root}}/host/config/resources/edit/">Resources</a>
        <span class="tab-line"></span>
    </div>

{% endblock %}