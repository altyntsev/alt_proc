{%- macro datepicker(name, label='') -%}
    {% if label != '' %}
        <label>{{ label }}</label>
    {% endif %}
    <div class="input-group dp-group">
        <span class="input-group-label igbutton dp-left"><i class="fa fa-caret-left"></i></span>
        <input type="text" class="form-control" name="{{ name }}" data-select="datepicker">
        <span class="input-group-label igbutton dp-right"><i class="fa fa-caret-right"></i></span>
        <span class="input-group-label igbutton dp-btn" data-toggle="datepicker"><i class="fa fa-calendar"></i></span>
        <span class="input-group-label igbutton dp-today"><i class="fa fa-calendar-check-o"></i></span>
    </div>
{%- endmacro %}

{%- macro checkbox(name, label='', id='', value='true') -%}
    <input type="checkbox" name="{{ name }}" value="{{ value }}" id="{%
            if id != '' %}{{ id }}{% else %}{{ name }}{% endif %}">
    {% if label !='' %}<label for="{%
            if id != '' %}{{ id }}{% else %}{{ name }}{% endif %}">{{ label }}</label>{% endif %}
{%- endmacro %}

{%- macro droplist(name, label='', values=[]) -%}
    <label>{{ label if label != '' }}</label>
    <select name="{{ name }}">
    {% for value in values %}
        {% if  value | length > 1  %}
            <option value="{{ value[0] }}">{{ value[1] }}</option>
        {% else %}
            <option value="{{ value }}">{{ value }}</option>
        {% endif %}
    {% endfor %}
    </select>
{%- endmacro %}

{%- macro radio(name, values=[]) -%}
    {% for value in values %}
        {% if  value | length > 1  %}
            <input type="radio" name="{{ name }}" value="{{ value[0] }}" id="{{ name ~ value[0] }}">
            <label for="{{ name ~ value[0] }}">{{ value[1] }}</label>
        {% else %}
            <input type="radio" name="{{ name }}" value="{{ value }}" id="{{ name ~ value }}">
            <label for="{{ name ~ value }}">{{ value }}</label>
        {% endif %}
    {% endfor %}
{%- endmacro %}

{%- macro select(name, values=[]) -%}
    <select name="{{ name }}">
    {% for value in values %}
        {% if  value | length > 1  %}
            <option value="{{ value[0] }}">{{ value[1] }}</option>
        {% else %}
            <option value="{{ value }}">{{ value }}</option>
        {% endif %}
    {% endfor %}
    </select>
{%- endmacro %}


