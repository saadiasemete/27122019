import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, MetaData
from werkzeug.security import generate_password_hash, check_password_hash

meta = MetaData()

Base = declarative_base()

class Board(Base):
    __tablename__ = "board"
    metadata = meta
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    address = Column(String(32), nullable=False)
    description = Column(String(256))
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean, default=False)
    admin_only = Column(Boolean, default=False)
    read_only = Column(Boolean, default=False)
    
class Post(Base):
    __tablename__ = "post"
    metadata = meta
    id = Column(Integer, primary_key=True)

    #number_in_thread = Column(Integer, nullable=False)

    board_id = Column(Integer, ForeignKey('tripcode.id'), nullable = False)

    reply_to = Column(Integer)

    ip_address = Column(String(16), nullable=False)

    title = Column(String(70))
    text = Column(String(8192))

    tripcode_id = Column(Integer, ForeignKey('tripcode.id')) #foreign key, actually - also nullable
    
    password_hash = Column(String(128))

    to_thread = Column(Integer, default = 0)
    sage = Column(Boolean)

    timestamp = Column(DateTime, nullable=False)
    timestamp_last_bump = Column(DateTime) #i just thought it would be too resource-consuming to compute it every time otherwise

    #https://dev.to/kaelscion/authentication-hashing-in-sqlalchemy-1bem

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(Base):
    __tablename__ = "admin"
    metadata = meta
    id = Column(Integer, primary_key=True)
    is_master = Column(Boolean, nullable=False)
    username = Column(String(32), nullable=False)
    login = Column(String(32), nullable=False)
    password_hash = Column(String(128), nullable=False)
    board_id = Column(Integer, ForeignKey('board.id')) #foreign key, actually - also nullable
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Tripcode(Base):
    __tablename__ = "tripcode"
    metadata = meta
    id = Column(Integer, primary_key=True)
    login = Column(String(32), nullable=False)
    password_hash = Column(String(128), nullable=False)
    represent = Column(String(32))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ban(Base):
    __tablename__ = "ban"
    metadata = meta
    id = Column(Integer, primary_key=True)

    board_id = Column(Integer, ForeignKey('board.id')) #foreign key, actually - also nullable

    thread_id = Column(Integer, ForeignKey('post.id')) #foreign key, actually - also nullable

    ip_address = Column(String(16), nullable=False)

    expires_at = Column(DateTime) #nullified => ban is eternal


class Captcha(Base):
    __tablename__ = "captcha"
    metadata = meta
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=False)
    answer = Column(String(32), nullable=False)

    ip_address = Column(String(16), nullable=False)

    timestamp = Column(DateTime, nullable=False) #nullified => captcha is eternal
