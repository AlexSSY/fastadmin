from sqlalchemy import create_engine, Integer, String, Column, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


engine = create_engine("sqlite:///./database.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=255), unique=True, index=True)
    password_digest = Column(String)

    animals = relationship('Animal', back_populates='owner')


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), unique=True, index=True)
    age = Column(Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='animals')
