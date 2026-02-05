# from enum import Enum as E

from sqlalchemy import (
  Column,
  Integer,
  String,
  # Enum,
  ForeignKey,
  UUID,
  DateTime,
)
from sqlalchemy.dialects.postgresql import CITEXT, BOOLEAN
from sqlalchemy.orm import relationship
from sealy.db.base import Base


# class UserType(E):
#   organization = 0
#   team = 1
#   individual = 2


class User(Base):
  __tablename__ = "users"

  # id = Column(Integer, Sequence("user_id_seq", start=0), primary_key=True)
  id = Column(UUID, primary_key=True)
  user_type = Column(Integer, nullable=False)
  parent_id = Column(UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
  username = Column(String, nullable=False)
  display_name = Column(String, nullable=True)  # i dunno. redundant?!
  email = Column(CITEXT, unique=True, index=True)
  is_active = Column(BOOLEAN, nullable=False)
  is_system = Column(BOOLEAN, nullable=False)
  timezone = Column(String, nullable=True)
  locale = Column(String, nullable=True)
  created_at = Column(DateTime(timezone=True), nullable=False)
  updated_at = Column(DateTime(timezone=True), nullable=False)
  deleted_at = Column(DateTime(timezone=True), nullable=True)

  # facilitate back to back ref. use passive_deletes with on delete set null
  parent = relationship(
    "User", remote_side=[id], backref="children", passive_deletes=True
  )
