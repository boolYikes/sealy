from enum import Enum as E

from sqlalchemy import (
  Column,
  String,
  Enum,
  ForeignKey,
  UUID,
  DateTime,
  func,
  CheckConstraint,
  Index,
  text,
)
from sqlalchemy.dialects.postgresql import CITEXT, BOOLEAN
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sealy.db.base import Base


class UserType(E):
  organization = "organization"
  team = "team"
  individual = "individual"


class User(Base):
  __tablename__ = "users"

  id = Column(UUID, primary_key=True)
  user_type: Mapped[UserType] = mapped_column(
    Enum(UserType, name="user_type"), nullable=False
  )
  parent_id = Column(UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
  username = Column(String, nullable=False)
  display_name = Column(String, nullable=True)  # i dunno. redundant?!
  email = Column(CITEXT, unique=True, index=True)
  is_active = Column(BOOLEAN, nullable=False, server_default=text("true"))
  is_system = Column(BOOLEAN, nullable=False, server_default=text("false"))
  timezone = Column(String, nullable=True)
  locale = Column(String, nullable=True)
  created_at = Column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at = Column(
    DateTime(timezone=True),
    nullable=False,
    onupdate=func.now(),
    server_default=func.now(),
  )
  deleted_at = Column(DateTime(timezone=True), nullable=True)

  # facilitate back to back ref. use passive_deletes with on delete set null
  parent = relationship(
    "User",
    remote_side=[id],
    backref="children",
    passive_deletes=True,
  )
  auths = relationship("AuthIdentity", back_populates="user")
  todos = relationship(
    "Todo", back_populates="user"
  )  # back populates the user relationship from the Todos table
  tags = relationship("Tag", back_populates="user")


# TBD
class Provider(E):
  password = "password"
  google = "google"
  apple = "apple"


class AuthIdentity(Base):
  __tablename__ = "auth_identities"

  id = Column(UUID, primary_key=True)
  user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  provider: Mapped[Provider] = mapped_column(
    Enum(Provider, name="provider"), nullable=False
  )
  provider_user_id = Column(String, nullable=True)
  password_hash = Column(String, nullable=True)
  email = Column(CITEXT, nullable=True)
  is_primary = Column(
    BOOLEAN, nullable=False, default=False, server_default=text("false")
  )
  created_at = Column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at = Column(
    DateTime(timezone=True),
    nullable=False,
    onupdate=func.now(),
    server_default=func.now(),
  )

  user = relationship("User", back_populates="auths")

  __table_args__ = (
    CheckConstraint(
      "(email IS NOT NULL AND password_hash IS NOT NULL) OR (provider IS NOT NULL AND provider_user_id IS NOT NULL)",
      name="auth_identity_check",
    ),
    Index(
      "idx_auth_provider_uid",
      "provider",
      "provider_user_id",
      unique=True,
      postgresql_where=text("provider_user_id IS NOT NULL"),
    ),
  )
