{% extends 'main.tpl' %}
{% block head %}
    <script>$$.menu_id='.menu-config';</script>
{% endblock %}

{% block submenu %}

    <div class="tab-list">
        <span class="tab-line"></span>
        <a class="tab submenu-hosts" href="{{_root}}/config/hosts/">Hosts</a>
        <span class="tab-line"></span>
    </div>

{% endblock %}