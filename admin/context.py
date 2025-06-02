class ModelAdminProcessor(ContextProcessor):

    @staticmethod
    def get_context(obj):
        return {
            'name': obj.Meta.model,
            'list_display': obj.list_display
        }
