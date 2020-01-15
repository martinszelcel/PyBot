from db import Base
from sqlalchemy import Column, Integer

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    level = Column(Integer, default=0)
    exp = Column(Integer, default=0)

    def __init__(self, discord_id):
        self.id = discord_id
