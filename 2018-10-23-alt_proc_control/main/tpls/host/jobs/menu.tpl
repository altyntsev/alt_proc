{% extends 'main.tpl' %}

{% block head %}
    <script>$$.menu_id='.menu-jobs';</script>
{% endblock %}

{% block submenu %}

    <div class="tab-list">
        <span class="tab-line"></span>
        <a class="tab menu-last" href="{{_root}}/host/jobs/last/">Last</a>
        <a class="tab menu-active" href="{{_root}}/host/jobs/active/">Active</a>
        <a class="tab menu-date" href="{{_root}}/host/jobs/date/?date={{ today }}">Date</a>
        <a class="tab menu-param" href="{{_root}}/host/jobs/param/">Parameter</a>
        <span class="tab-line"></span>
    </div>

{% endblock %}