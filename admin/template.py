class TemplateBase:

    def render_to_string(template_name, **context):
        raise NotImplementedError()

    def add_global(fn, *args, **kwargs):
        raise NotImplementedError()
    
    def register_templates_paths(*paths):
        raise NotImplementedError()
    
    def render_to_response(request, template_name, context={}):
        raise NotImplementedError()
