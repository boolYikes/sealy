from enum import Enum as E

from sqlalchemy import Column, Integer, String, Sequence, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sealy.db.base import Base


class UserType(E):
  auth_user = 0
  organization = 1
  team = 2
  individual = 3


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, Sequence("user_id_seq", start=0), primary_key=True)
  username = Column(String, nullable=False)
  user_type = Column(Enum(UserType), nullable=False)
  email = Column(String, unique=True, index=True)
  parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)

  # facilitate back to back ref
  parent = relationship("User", remote_side=[id], backref="children")
