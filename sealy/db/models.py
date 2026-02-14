# TODO: Move IntEnum mapper to api side + add mapper for recurrence_type
# TODO: Use DB level trigger for updated_at! onupdate is ORM level!
# TODO: Enforce column level permission on admin-related elements (is_system)
# NOTE: Consider evolution strategy for zero downtime(alter table uses ACCESS EXCLUSIVE)

from enum import Enum as E, IntEnum

from sqlalchemy import (
  Column,
  Integer,
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
from sqlalchemy.dialects.postgresql import CITEXT, BOOLEAN, ARRAY
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


class Priority(IntEnum):
  none = 0
  low = 1
  medium = 2
  high = 3
  urgent = 4


class Todo(Base):
  __tablename__ = "todos"

  id = Column(UUID, primary_key=True)
  title = Column(String(200), nullable=False)
  priority = Column(Integer, nullable=False, default=0, server_default=text("0"))
  pinned = Column(BOOLEAN, nullable=False, default=False, server_default=text("false"))
  done = Column(BOOLEAN, nullable=False, default=False, server_default=text("false"))
  description = Column(String, nullable=True)
  deadline = Column(DateTime(timezone=True), nullable=True)
  user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  parent_id = Column(UUID, ForeignKey("todos.id", ondelete="SET NULL"), nullable=True)
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

  user = relationship("User", back_populates="todos")
  parent = relationship(
    "Todo", remote_side=[id], backref="children", passive_deletes=True
  )
  recurrence = relationship("TodoRecurrence", back_populates="todo")


# Ref: todos.id - shared_todos.todo_id [delete: cascade]
# Ref: todos.id < todos_tags.todo_id [delete: cascade]


class TodoRecurrence(Base):
  __tablename__ = "todo_recurrences"
  """
  recurrence_type does not GATE how it works but how these columns are interpreted
  ### recurrence_type mapping:
  - daily = 0
  - weekly = 1
  - monthly = 2
  - yearly = 3
  """
  id = Column(UUID, primary_key=True)
  # unique -> one to one rel
  todo_id = Column(
    UUID, ForeignKey("todos.id", ondelete="CASCADE"), unique=True, nullable=False
  )
  recurrence_type = Column(Integer, nullable=True)
  interval = Column(Integer, nullable=True)  # for all types
  days_of_week = Column(ARRAY(Integer), nullable=True)  # 0-6: Sun-Sat
  days_of_month = Column(ARRAY(Integer), nullable=True)  # 1-31 with -1 as the last day
  weeks_of_month = Column(ARRAY(Integer), nullable=True)  # 1-5 with -1 for last week
  months_of_year = Column(ARRAY(Integer), nullable=True)  # 1-12
  start_at = Column(
    DateTime(timezone=True), nullable=False
  )  # Should be user local time
  end_at = Column(DateTime(timezone=True), nullable=True)  # null: no end
  created_at = Column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at = Column(
    DateTime(timezone=True),
    nullable=False,
    onupdate=func.now(),
    server_default=func.now(),
  )

  todo = relationship("Todo", back_populates="recurrence")

  # or use conditionals...
  __table_args__ = (
    CheckConstraint(
      """
      (
        recurrence_type IS NULL
        AND interval IS NULL
        AND days_of_week IS NULL
        AND days_of_month IS NULL
        AND weeks_of_month IS NULL
        AND months_of_year IS NULL
      )
      OR
      (
        recurrence_type IS NOT NULL
        AND interval IS NOT NULL
        AND
        (
          (
            days_of_week IS NULL
            AND days_of_month IS NULL
            AND weeks_of_month IS NULL
            AND months_of_year IS NULL
          )
          OR
          (
            (days_of_week IS NOT NULL)::int +
            (days_of_month IS NOT NULL)::int +
            (weeks_of_month IS NOT NULL)::int +
            (months_of_year IS NOT NULL)::int
          ) = 1
        )
      )
      """,
      name="todo_recurrence_check",
    ),
  )
