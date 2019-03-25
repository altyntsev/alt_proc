<table>
    <thead><tr>
        <th>id</th><th>mtime</th><th>task</th><th>param</th><th>status</th><th>result</th>
        <th>scripts</th><th>wtime</th><th>messages</th>
    </tr></thead>
    {% for job in jobs %}
        <tr>
            <td>{{job.job_id}}</td>
            <td>{{job.mtime}}</td>
            <td>{{job.task}}</td>
            {% if job.type=='PERIODIC' %}
                <td class="tac"><i class="fa fa-hourglass"></i></td>
            {% else %}
                <td nowrap>{{job.param}}</td>
            {% endif %}

            {% if not job.result %}
                <td class="{{job.status}} tac" colspan="2">{{job.status}}</td>
            {% elif job.status=='DONE' %}
                {% if job.todo %}
                    <td class="TODO tac" colspan="2">{{job.result}}</td>
                {% else %}
                    <td class="{{job.result}} tac" colspan="2">{{job.result}}</td>
                {% endif %}
            {% else %}
                <td class="{{job.status}} tac">{{job.status}}</td>
                {% if job.todo %}
                    <td class="TODO tac">{{job.result}}</td>
                {% else %}
                    <td class="{{job.result}} tac">{{job.result}}</td>
                {% endif %}
            {% endif %}

            <td onclick="window.location.href='{{_root}}/host/job/{{job.job_id}}/';">
                {% for script in job.scripts %}
                    <span class="{{script.status}}_{{script.result}} script">{{script.name}}</span>
                {% endfor %}
            </td>
            <td>{{job.wtime if job.wtime!=None}}</td>
            <td>
                {% for msg in job.msgs %}
                    {% if msg.n_runs>1 %}
                        {{msg.n_runs}} {{msg.stime_diff}}
                    {% endif %}
                    {{msg.msg}}
                {% endfor %}
            </td>
        </tr>
    {% endfor %}
</table>

