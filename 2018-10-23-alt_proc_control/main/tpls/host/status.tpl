{% extends "main.tpl" %}
{% block head %}
    <script>$$.menu_id='.menu-status';</script>
    <script>
        function refresh(){
                $.ajax({
                    url: '{{ _root }}/host/status_ajax/',
                    success: function (response) {
                        response = JSON.parse(response);
                        $('#html_ajax').html(response.html);
                        $('#now').html(response.now);
                        initSelectArrowOnly();
                        $("#ajax_status").html('');
                    }
                });
            };
        $(function () {
            refresh();
            setInterval(refresh,60000);
        });
    </script>
{% endblock %}
{% block content %}

    <div id="html_ajax"></div>

{% endblock %}