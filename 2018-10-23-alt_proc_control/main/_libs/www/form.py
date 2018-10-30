from alt.dict_ import dict_
import json
import cherrypy

def prepare_form(form, default=None):

    if isinstance(form, dict):
        form = dict_(form)
        if default:
            for key, value in default.items():
                if key not in form:
                    form[key] = value

    if isinstance(form, str):
        form = dict_(json.loads(form))

    if cherrypy.request.method=='GET':
        for key, value in form.items():
            if value=='true':
                form[key] = True
            if value=='false':
                form[key] = False

    return form
