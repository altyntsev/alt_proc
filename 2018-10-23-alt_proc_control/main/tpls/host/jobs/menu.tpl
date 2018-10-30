{% extends 'main.tpl' %}

{% block head %}
    <script>$$.menu_id='.menu-jobs';</script>
{% endblock %}

{% block submenu %}

    <div class="tab-list">
        <span class="tab-line"></span>
        <a class="tab menu-last" href="{{_root}}/host/jobs/last/{{ host }}">Last</a>
        <a class="tab menu-active" href="{{_root}}/jobs/active/">Active</a>
        <a class="tab menu-date" href="{{_root}}/jobs/date/">Date</a>
        <a class="tab menu-key" href="{{_root}}/jobs/key/">Key</a>
        <span class="tab-line"></span>
    </div>

{% endblock %}