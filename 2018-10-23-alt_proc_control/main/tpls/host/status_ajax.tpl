<form>
    <div class="grid-x grid-padding-x">
        <label>Host:</label>
        <div class="{{ host_status }}" style="padding:0 0 0 0.5rem;">
            <span>{{ host_status }}</span>
            <select data-arrow-only name="host_status"
                    onchange="send_cmd('SET_HOST_STATUS', {status: $(this).val()})">
                <option {% if host_status == 'RUN'  %}selected{% endif %} value="RUN">RUN</option>
                <option {% if host_status == 'PAUSE'  %}selected{% endif %} value="PAUSE">PAUSE</option>
                <option {% if host_status == 'EXIT'  %}selected{% endif %} value="EXIT">EXIT</option>
            </select>
        </div>
        <div class="large-1">
            {{ manager_mtime }}
        </div>
        {% if repl_status %}
            <div class="{{ repl_status }}">Replication</div>
        {% endif %}
    </div>
</form>

{% if msgs %}
    <div style="height: 5rem; overflow-y: auto; display:inline-block; border:2px solid #335c32;">
        <table>
            <thead>
                <th>mtime</th><th>time</th><th>job_id</th><th>type</th>
                <th>msg</th><th>task</th><th>key</th><th>script</th><th>read</th>
            </thead>
            {% for msg in msgs %}
                <tr {% if not msg.active %}style="background-color: lightgrey;"{% endif %}>
                    <td>{{msg.mtime}}</td>
                    <td>{{msg.stime}} - {{msg.etime}} / {{ msg.diff }} {{ msg.n_runs }}</td>
                    <td>{{msg.job_id}}</td>
                    {% if msg.todo %}
                        <td class="TODO">{{msg.type}}</td>
                    {% else %}
                        <td class="{{ msg.type }}">{{msg.type}}</td>
                    {% endif %}
                    <td>{{msg.msg}}</td>
                    <td>{{msg.name}}</td>
                    <td>{{msg.key}}</td>
                    <td>{{msg.cmd}}</td>
                    <td>
                        {% if not msg.read %}
                            <input type="button" value="OK" onclick="msg_read([{{ msg.id }}],this)" />
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>
{% endif %}

<table>
    <thead><tr>
        <th>project</th>
        <th>task</th>
        <th style="background-color: yellow" colspan="4">WAIT</th>
        <th style="background-color: green; color: white;" colspan="3">RUN</th>
        <th style="background-color: #335c32;  color: white;" colspan="3">DONE</th>
        <th style="background-color: #335c32;  color: white;" colspan="3">PREV</th>
        <th style="background-color: #335c32;  color: white;" colspan="2">ERR</th>
        <th>mtime</th><th>param</th><th>status</th><th>result</th><th>scripts</th>
        <th>wtime</th><th>messages</th>
    </tr></thead>
    {% for task in tasks %}
        <tr>
            <td>{{ task.project }}</td>
            <td class="{{ task.status }}">
                <span>{{task.name}}</span>
                <select data-arrow-only name="task_status_{{ task.name }}"
                    onchange="send_cmd('SET_TASK_STATUS', { task_id:{{ task.id }}, status: $(this).val() });"
                >
                    <option {% if task.status == 'ACTIVE' %}selected{% endif %} value="ACTIVE">ACTIVE</option>
                    <option {% if task.status == 'PAUSE'  %}selected{% endif %} value="PAUSE">PAUSE</option>
                    <option {% if task.status == 'DEBUG'  %}selected{% endif %} value="DEBUG">DEBUG</option>
                </select>
            </td>
            {% include 'host/status_table.tpl' %}
        </tr>
    {% endfor %}
</table>

