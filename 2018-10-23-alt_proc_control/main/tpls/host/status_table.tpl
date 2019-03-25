{% if task.type=='EVENT' %}

    {% if task.events %}
        <td class="EVENTS">{{task.events}}</td>
    {% else %}
        <td></td>
    {% endif %}

    {% if task.wait %}
        <td class="WAIT">{{task.wait}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {% if task.wait_fatal %}
        <td class="WAIT_FATAL">{{task.wait_fatal}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {% if task.wait_todo %}
        <td class="WAIT_TODO">{{task.wait_todo}}</td>
    {% else %}
        <td></td>
    {% endif %}

    {% if task.run %}
        <td class="RUN">{{task.run}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {% if task.run_fatal %}
        <td class="RUN_FATAL">{{task.run_fatal}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {% if task.run_todo %}
        <td class="RUN_TODO">{{task.run_todo}}</td>
    {% else %}
        <td></td>
    {% endif %}

    {% if task.done %}
        <td class="SUCCESS">{{task.done}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {% if task.done_fatal %}
        <td class="DONE_FATAL">{{task.done_fatal}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {%  if task.done_todo %}
        <td class="TODO">{{task.done_todo}}</td>
    {% else %}
        <td></td>
    {% endif %}

    {% if task.done_prev %}
        <td class="SUCCESS">{{task.done_prev}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {% if task.done_fatal_prev %}
        <td class="DONE_FATAL">{{task.done_fatal_prev}}</td>
    {% else %}
        <td></td>
    {% endif %}
    {%  if task.done_todo_prev %}
        <td class="TODO">{{task.done_todo_prev}}</td>
    {% else %}
        <td></td>
    {% endif %}

{% else %}

    <td colspan="13">
        <i class="hourglass full icon"></i>
        {{ task.period }}
    </td>

{% endif %}

{%  if task.errors not in [0,None] %}
    <td class="ERROR">{{task.errors}}</td>
{% else %}
    <td></td>
{% endif %}
{%  if task.errors_todo not in [0,None] %}
    <td class="TODO">{{task.errors_todo}}</td>
{% else %}
    <td></td>
{% endif %}

{% if 'job' in task %}
    {% set job=task.job %}
    <td>{{job.mtime_diff}}</td>
    <td>{{job.param if job.param!=None}}</td>
    {% if not job.result %}
        <td class="{{job.status}}" colspan="2">{{job.status}}</td>
    {% elif job.status=='DONE' %}
        {% if job.todo %}
            <td class="TODO" colspan="2">{{job.result}}</td>
        {% else %}
            <td class="{{job.result}}" colspan="2">{{job.result}}</td>
        {% endif %}
    {% else %}
        <td class="{{job.status}}">{{job.status}}</td>
        {% if job.todo %}
            <td class="TODO">{{job.result}}</td>
        {% else %}
            <td class="{{job.result}}">{{job.result}}</td>
        {% endif %}
    {% endif %}
    <td class="left aligned" style="padding: 0;"
        onclick="window.location.href='{{ _root }}/host/job/{{ job.job_id }}/'">
        {% for script in job.scripts %}
            <div class="{{script.status}}_{{script.result}} script">
                {{script.name}}</div>
        {% endfor %}
    </td>
    <td>{{job.wtime if job.wtime!=None}}</td>
    <td style="padding: 2px;">
        {% for msg in job.msgs %}
            {% if msg.n_runs>1 %}
                {{msg.n_runs}} {{msg.stime_diff}}
            {% endif %}
            {{msg.msg}}
        {% endfor %}
    </td>
{% endif %}
