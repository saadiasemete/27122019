import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()

class Board(Base):
    ___tablename__ = "board"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    address = Column(String(32), nullable=False)
    hidden = Column(Boolean, default=False)
    admin_only = Column(Boolean, default=False)
    read_only = Column(Boolean, default=False)
    
class Post(Base):
    ___tablename__ = "post"
    id = Column(Integer, primary_key=True)
    id_board = Column(Integer)
    id_thread = Column(Integer, nullable=False)

    title = Column(String(70))
    text = Column(String(8192))

    tripcode_id = Column(Integer, ForeignKey('tripcode.id')) #foreign key, actually - also nullable
    tripcode = relationship("Tripcode", back_populates="post")
    
    password_hash = Column(String(128))


    #one or the other must be fulfilled
    is_thread = Column(Boolean, nullable=False)
    
    to_thread = Column(Integer)
    sage = Column(Boolean)

    timestamp = Column(DateTime, nullable=False)
    timestamp_last_bump = Column(DateTime) #i just thought it would be too resource-consuming to compute it every time otherwise

    #https://dev.to/kaelscion/authentication-hashing-in-sqlalchemy-1bem

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(Base):
    ___tablename__ = "admin"
    id = Column(Integer, primary_key=True)
    is_master = Column(Boolean, nullable=False)
    username = Column(String(32), nullable=False)
    login = Column(String(32), nullable=False)
    password_hash = Column(String(128), nullable=False)
    board_id = Column(Integer, ForeignKey('board.id')) #foreign key, actually - also nullable
    board = relationship("Board", back_populates="admin")
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Tripcode(Base):
    ___tablename__ = "tripcode"
    id = Column(Integer, primary_key=True)
    login = Column(String(32), nullable=False)
    password_hash = Column(String(128), nullable=False)
    represent = Column(String(32))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)