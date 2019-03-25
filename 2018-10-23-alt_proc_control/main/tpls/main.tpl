<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>alt_proc control</title>

    <script src="{{_root}}/static/jquery/jquery-3.1.1.min.js" type="text/javascript"></script>
    <link rel="stylesheet" href="{{_root}}/static/foundation/foundation.css">
    <script src="{{_root}}/static/foundation/foundation.min.js" type="text/javascript"></script>
    <link href="{{_root}}/static/awesome/font-awesome.css" rel="stylesheet">
    <link href="{{_root}}/static/datepicker/jquery.datepicker.css" rel="stylesheet">
    <script src="{{_root}}/static/datepicker/jquery.datepicker.js" type="text/javascript"></script>

    <link href="{{_root}}/static/snm/snm.css" rel="stylesheet">
    <link href="{{_root}}/static/snm/main.css" rel="stylesheet">
    <script src="{{_root}}/static/snm/snm.js" type="text/javascript"></script>
    <script src="{{_root}}/static/snm/main.js" type="text/javascript"></script>

    <link href="{{_root}}/static/scanex/main.css" rel="stylesheet">
    <link href="{{_root}}/static/scanex/status.css" rel="stylesheet">
    <script src="{{_root}}/static/scanex/main.js" type="text/javascript"></script>

    <link href="{{_root}}/static/main.css" rel="stylesheet">
    <script src="{{_root}}/static/main.js" type="text/javascript"></script>

    <script>
        $.extend($$,{{ _form }});
        $$._root = '{{ _root }}';
    </script>
    {% block head %}{% endblock %}
</head>
<body>
<div class="top-bar">

    <div class="top-bar-left">
        <ul class="menu">
            <li><a class="menu-logo" href="{{_root}}/">alt_proc</a></li>
            <li><a class="menu-status" href="{{_root}}/host/status/">Status</a></li>
            <li><a class="menu-jobs" href="{{_root}}/host/jobs/last/">Jobs</a></li>
            <li><a class="menu-msgs" href="{{_root}}/host/msgs/">Messages</a></li>
            <li><a class="menu-config" href="{{_root}}/host/config/task/list/">Config</a></li>
            {% if n_cmds!=0 %}
                <li><span class="menu-text" style="color: red;">{{ n_cmds }} !</span></li>
            {% endif %}
            <li><span id="ajax_status" class="menu-text"></span></li>
        </ul>
    </div>

    <div class="top-bar-right">
        <ul class="menu">
            <li><a id="now" style="color: yellow;"
                   onclick="window.location.reload(true);">{{ now }}</a></li>
            <li class="right"><a class="menu-user" href="" onclick="logout()">[{{ _user }}]</a></li>
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

