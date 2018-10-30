<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>alt_proc</title>

    <script src="{{root}}/static/jquery/jquery-3.1.1.min.js" type="text/javascript"></script>
    <link rel="stylesheet" href="{{root}}/static/foundation/foundation.css">
    <script src="{{root}}/static/foundation/foundation.min.js" type="text/javascript"></script>
    <link href="{{root}}/static/awesome/font-awesome.css" rel="stylesheet">
    <link href="{{root}}/static/datepicker/jquery.datepicker.css" rel="stylesheet">
    <script src="{{root}}/static/datepicker/jquery.datepicker.js" type="text/javascript"></script>

    <link href="{{root}}/static/snm/snm.css" rel="stylesheet">
    <link href="{{root}}/static/snm/main.css" rel="stylesheet">
    <script src="{{root}}/static/snm/snm.js" type="text/javascript"></script>
    <script src="{{root}}/static/snm/main.js" type="text/javascript"></script>

    <link href="{{root}}/static/scanex/main.css" rel="stylesheet">
    <link href="{{root}}/static/scanex/status.css" rel="stylesheet">
    <script src="{{root}}/static/scanex/main.js" type="text/javascript"></script>

    <link href="{{root}}/static/main.css" rel="stylesheet">
    <script src="{{root}}/static/main.js" type="text/javascript"></script>

    <script>
        $.extend($$,{{ _form }});
        $$._root = '{{ _root }}';
        $$.host = '{{ host }}';
    </script>
    {% block head %}{% endblock %}
</head>
<body>
<div class="top-bar">

    <div class="top-bar-left">
        <ul class="menu">
            {% if hub_mode %}
                <select name="host" id="host" onchange="switch_host();">
                    <option value="hub">HUB</option>
                    {% for host in hosts.keys() %}
                        <option value="{{ host }}">{{ host }}</option>
                    {% endfor %}
                </select>
            {% else %}
                <li><a class="menu-logo" href="{{_root}}/">alt_proc</a></li>
            {% endif %}
            {% if host=='hub' %}
                <li><a class="menu-status" href="{{_root}}/status/">Status</a></li>
                <li><a class="menu-msgs" href="{{_root}}/msgs/">Messages</a></li>
                <li><a class="menu-config" href="{{_root}}/config/hosts/">Config</a></li>
            {% else %}
                <li><a class="menu-status" href="{{_root}}/host/status/{{host}}/">Status</a></li>
                <li><a class="menu-jobs" href="{{_root}}/host/jobs/last/{{host}}/">Jobs</a></li>
                <li><a class="menu-msgs" href="{{_root}}/host/msgs/{{host}}/">Messages</a></li>
                <li><a class="menu-config" href="{{_root}}/host/config/tasks/{{host}}/">Config</a></li>
            {% endif %}
            <li><span id="ajax_status" class="menu-text"></span></li>
        </ul>
    </div>

    <div class="top-bar-right">
        <ul class="menu">
            <li><a id="now" style="color: yellow;"
                   onclick="window.location.reload(true);">{{ now }}</a></li>
            <li class="right"><a class="menu-user" href="{{ root }}/user/profile/">[{{ _user }}]</a></li>
        </ul>
    </div>
</div>

{% block submenu %}{% endblock %}

<div id="err-callout" class="callout alert {% if not error %}hidden{% endif %}" data-closable>
    <button class="close-button" aria-label="Close alert" type="button" data-close>
        <span aria-hidden="true">&times;</span>
    </button>
    <div id="err"><p>{{ error }}</p></div>
</div>

{% block content %}{% endblock %}


</body>

</html>

