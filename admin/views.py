from .bases import View


class DashboardView:
    template = None
    methods = ['get']

    def get_context(self):
        ...

    def get_response(self):
        ...