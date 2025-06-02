class ModelAdmin:
    class Meta:
        pass

    fields = '__all__' # form fields; can be list[str] or list[dict[str, str]]
    readonly_fields = [] # form readonly fields
    list_display = '__all__' # list of fields on the index page; can be list[str]


class Record:
    pass


class View:
    class Meta:
        ...

    def get_context(self):
        raise NotImplementedError()


class ModelView(View):
    class Meta:
        model = None

    def get_context(self):
        return {}