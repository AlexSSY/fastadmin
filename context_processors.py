from bases import ContextProcessor


class ModelContextProcessor(ContextProcessor):

    def get_context(self, obj):
        context = {}

        meta = obj.Meta
        name = getattr(meta, 'name', obj.__name__)
        context.update({ 'name': name })

        return context


class ModelRecordsContextProcessor:
    ...
