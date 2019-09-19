from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base


class Record(declarative_base()):
    __tablename__ = 'snapnews_record'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    channel = Column(String(30))
    time = Column(DateTime)
    keyword = Column(String(50))
    image = Column(String(50))
    user_id = Column(Integer)

    def __str__(self):
        return self.channel


class Channel(declarative_base()):
    __tablename__ = 'setting_channel'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    url = Column(String(50))
    name = Column(String(20))
    enable = Column(Boolean)

    def __str__(self):
        return self.name


class Keyword(declarative_base()):
    __tablename__ = 'myaccount_userkeyword'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    keyword = Column(String(30))
    user_id = Column(Integer)

    def __str__(self):
        return self.keyword


class UserProfile(declarative_base()):
    __tablename__ = 'myaccount_userprofile'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    org = Column(String(128))
    telephone = Column(String(50))
    line_api_key = Column(String(100))
    email_address = Column(String(100))
    mod_date = Column(DateTime)
    user_id = Column(Integer)

    def __str__(self):
        return self.user_id
