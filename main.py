import uvicorn
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import db
from admin import Admin, AdminModel


app = FastAPI()
admin = Admin(app, db.engine)

class UserAdmin(AdminModel):
    model = db.User
    fields = ['id', 'email', 'spagetti', 'email_and_id']

    def spagetti(self, obj):
        return "Кастомное значение"
        
    def email_and_id(self, obj):
        return obj.email + "   " + str(obj.id)

admin.register(db.User, UserAdmin)

if __name__ == "__main__":
    db.Base.metadata.create_all(bind=db.engine)
    uvicorn.run("main:app", reload=False)
