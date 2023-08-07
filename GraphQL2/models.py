import os
import psycopg2
from sqlalchemy.orm import (
    scoped_session, relationship,
    sessionmaker
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import URL
from sqlalchemy import *
from dotenv import load_dotenv
load_dotenv()

HOST_DB = os.getenv('HOST_DB')
PORT_DB = os.getenv('PORT_DB')
USER_DB = os.getenv('USER_DB')
NAME_DB = os.getenv('NAME_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')

engine = create_engine(f"postgresql+psycopg2://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}")
session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)


Base = declarative_base()
Base.metadata.bind = engine
Base.query = session.query_property()


class Wishlists(Base):
    __tablename__ = 'wishlists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150))
    price = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship('Users', back_populates='wishlists')


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100))
    password = Column(String(200))
    wishlists = relationship('Wishlists', back_populates='users')
