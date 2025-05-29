class Indexable:
    
    def index(self, request):
        pass


class UserAuthorization:

    def can_index(self, request):
        return request.admin.user.role == "admin"
    
    def can_everything(self, request):
        return request.admin.user.role == "admin"
