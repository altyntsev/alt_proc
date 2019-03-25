<form>
    <div class="grid-x grid-padding-x">
        <label>Host:</label>
        <div class="{{ host_status }}">
            <span>{{ host_status }}</span>
            {% if 'admin' in _roles %}
                <select data-arrow-only name="host_status"
                        onchange="send_cmd('SET_HOST_STATUS', {status: $(this).val()})">
                    <option {% if host_status == 'RUN'  %}selected{% endif %} value="RUN">RUN</option>
                    <option {% if host_status == 'PAUSE'  %}selected{% endif %} value="PAUSE">PAUSE</option>
                    <option {% if host_status == 'EXIT'  %}selected{% endif %} value="EXIT">EXIT</option>
                </select>
            {% endif %}
        </div>
        <div class="large-1">
            {{ manager_mtime }}
        </div>
        {% if repl_status %}
            <div class="{{ repl_status }}">Replication</div>
        {% endif %}
    </div>
</form>

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
                {% if 'admin' in _roles %}
                    <select data-arrow-only name="task_status_{{ task.name }}"
                        onchange="send_cmd('SET_TASK_STATUS',
                                { task_id:{{ task.task_id }}, status: $(this).val() });"
                    >
                        <option {% if task.status == 'ACTIVE' %}selected{% endif %} value="ACTIVE">ACTIVE</option>
                        <option {% if task.status == 'PAUSE'  %}selected{% endif %} value="PAUSE">PAUSE</option>
                        <option {% if task.status == 'DEBUG'  %}selected{% endif %} value="DEBUG">DEBUG</option>
                        <option {% if task.status == 'TODO'  %}selected{% endif %} value="TODO">TODO</option>
                    </select>
                {% endif %}
            </td>
            {% include 'host/status_table.tpl' %}
        </tr>
    {% endfor %}
</table>

