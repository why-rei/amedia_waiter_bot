from sqlalchemy import ForeignKey, Column, Boolean, Integer, String, DateTime, BigInteger, SmallInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# class Users(Base):
#     __tablename__ = 'users'
#     id = Column(BigInteger(), primary_key=True, autoincrement=False)
#     date_start = Column(DateTime(), default=datetime.now(), nullable=True)
#     last_update = Column(DateTime(), nullable=True)
#     fav_count = Column(SmallInteger, default=0, nullable=True)


class Animes(Base):
    __tablename__ = 'animes'
    id = Column(Integer(), primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    desc = Column(Text, nullable=True)
    info = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    link = Column(String, nullable=True)


class LastAnimes(Base):
    __tablename__ = 'lastanimes'
    id = Column(Integer, nullable=False, primary_key=True)
    anime_id = Column(Integer, ForeignKey('animes.id'))
    seria = Column(String, nullable=True)
    time = Column(String, nullable=True)
    anime = relationship('Animes', uselist=False, lazy='joined')


class TodayAnimes(Base):
    __tablename__ = 'todayanimes'
    id = Column(Integer, nullable=False, primary_key=True)
    anime_id = Column(Integer, ForeignKey('animes.id'))
    seria = Column(String, nullable=True)
    time = Column(String, nullable=True)
    anime = relationship('Animes', uselist=False, lazy='joined')


class Ants(Base):
    __tablename__ = 'ants'
    id = Column(Integer, nullable=False, primary_key=True)
    anime_id = Column(Integer, ForeignKey('animes.id'))
    anime = relationship('Animes', uselist=False, lazy='joined')


class Timetable(Base):
    __tablename__ = 'timetable'
    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    anime_id = Column(Integer, ForeignKey('animes.id'))
    day = Column(SmallInteger, nullable=True)
    time = Column(String, nullable=True)
    anime = relationship('Animes', uselist=False, lazy='joined')

#
# class Notice(Base):
#     __tablename__ = 'notice'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     anime_id = Column(Integer, ForeignKey('animes.id'), nullable=False)
#     seria = Column(String, nullable=False)
#     checker = Column(Boolean, default=False)
#     anime = relationship('Animes', uselist=False, lazy='joined')
#
#
# class Favorite(Base):
#     __tablename__ = 'favorite'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'))
#     anime_id = Column(Integer, ForeignKey('animes.id'))
#     anime = relationship('Animes', uselist=False, lazy='joined')
#
#
