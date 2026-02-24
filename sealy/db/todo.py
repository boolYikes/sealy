from enum import IntEnum
from datetime import datetime
from uuid import UUID as uuid

from sqlalchemy import (
  Integer,
  String,
  ForeignKey,
  UUID,
  DateTime,
  func,
  CheckConstraint,
  text,
)
from sqlalchemy.dialects.postgresql import BOOLEAN, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sealy.db.base import Base


class Priority(IntEnum):
  none = 0
  low = 1
  medium = 2
  high = 3
  urgent = 4


class Todo(Base):
  __tablename__ = "todos"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  title: Mapped[str] = mapped_column(String(200), nullable=False)
  priority: Mapped[int] = mapped_column(
    Integer, nullable=False, default=0, server_default=text("0")
  )
  pinned: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, default=False, server_default=text("false")
  )
  done: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, default=False, server_default=text("false")
  )
  description: Mapped[str | None] = mapped_column(String, nullable=True)
  deadline: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  user_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
  )
  parent_id: Mapped[uuid | None] = mapped_column(
    UUID, ForeignKey("todos.id", ondelete="SET NULL"), nullable=True
  )
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    onupdate=func.now(),
    server_default=func.now(),
  )
  deleted_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )

  user = relationship("User", back_populates="todos")
  parent = relationship(
    "Todo", remote_side=[id], backref="children", passive_deletes=True
  )
  recurrence = relationship("TodoRecurrence", back_populates="todo")
  todo_tags = relationship("TodoTag", back_populates="todo")


# TODO: todos.id - shared_todos.todo_id [delete: cascade]


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
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  # unique -> one to one rel
  todo_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("todos.id", ondelete="CASCADE"), unique=True, nullable=False
  )
  recurrence_type: Mapped[int | None] = mapped_column(Integer, nullable=True)
  interval: Mapped[int | None] = mapped_column(Integer, nullable=True)  # for all types
  days_of_week: Mapped[list[int] | None] = mapped_column(
    ARRAY(Integer), nullable=True
  )  # 0-6: Sun-Sat
  days_of_month: Mapped[list[int] | None] = mapped_column(
    ARRAY(Integer), nullable=True
  )  # 1-31 with -1 as the last day
  weeks_of_month: Mapped[list[int] | None] = mapped_column(
    ARRAY(Integer), nullable=True
  )  # 1-5 with -1 for last week
  months_of_year: Mapped[list[int] | None] = mapped_column(
    ARRAY(Integer), nullable=True
  )  # 1-12
  start_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=False
  )  # Should be user local time
  end_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )  # null: no end
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at: Mapped[datetime] = mapped_column(
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
