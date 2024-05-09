import enum
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Todo(Base):
    __tablename__ = 'todos'
    id: int = Column(Integer, primary_key=True)
    title: str = Column(String(50), index=True)
    description: str = Column(String(250))
    completed: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", backref="todos", lazy="joined")


class Role(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(50))
    email: str = Column(String(150), nullable=False, unique=True)
    password: str = Column(String(255), nullable=False)
    avatar: str = Column(String(255), nullable=True)
    refresh_token: str = Column(String(255), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    role: Role = Column(Enum(Role), default=Role.user, nullable=True)
    confirmed: bool = Column(Boolean, default=False, nullable=True)
