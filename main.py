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
    fields = ['id', 'email', 'password_digest', 'spagetti', 'email_and_id']

    def field_id_name(self):
        return "ID"

    def field_spagetti_name(self):
        return "Спагетти"

    def spagetti(self, obj):
        return "Кастомное значение"
        
    def email_and_id(self, obj):
        return obj.email + "   " + str(obj.id)
    
    def field_email_and_id_name(self):
        return "Email и  ID"

admin.register(db.User, UserAdmin)

def seed():
    from faker import Faker

    fake = Faker()

    with db.SessionLocal() as session:
        for _ in range(0, 100):
            user = db.User(email=fake.email(safe=True), password_digest="password")
            session.add(user)
        session.commit()


if __name__ == "__main__":
    db.Base.metadata.create_all(bind=db.engine)
    # seed()
    uvicorn.run("main:app", reload=False)
