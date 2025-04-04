from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    profile_picture = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    watch_history = relationship("WatchHistory", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    content_id = Column(String(50))
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="watchlist")


class WatchHistory(Base):
    __tablename__ = "watch_history"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    content_id = Column(String(50), primary_key=True)
    watched_at = Column(DateTime, default=datetime.utcnow)
    # watch_duration = Column(Integer)  # How many seconds watched, dont work
    completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="watch_history")
