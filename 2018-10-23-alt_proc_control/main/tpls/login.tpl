{% extends "main.tpl" %}

{% block head %}
    {{ super() }}
    <script>$$.submenu_id='.menu-user';</script>
{% endblock %}

{% block content %}

    <div class="grid-x grid-padding-x align-center text-center">
        <div class="cell width200">
            <form method="post" data-ignore>
                <label>Логин:</label>
                <input class="white-bg" type="text" name="login">
                <label>Пароль:</label>
                <input class="white-bg" type="password" name="pwd">
                <input type="submit" value="Вход">
            </form>
        </div>
    </div>

{% endblock %}
