from uuid import UUID as uuid
from datetime import datetime

from sqlalchemy import (
  String,
  ForeignKey,
  UUID,
  DateTime,
  func,
  text,
  UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sealy.db.base import Base


class Tag(Base):
  __tablename__ = "tags"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  user_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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

  user = relationship("User", back_populates="tags")
  todo_tags = relationship("TodoTag", back_populates="tag", passive_deletes="all")
  contact_tags = relationship("ContactTag", back_populates="tag", passive_deletes="all")
  memo_tags = relationship("MemoTag", back_populates="tag", passive_deletes="all")


class TodoTag(Base):
  __tablename__ = "todo_tags"
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  todo_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False
  )
  tag_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
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

  # includes same tags from different todos.
  tag = relationship("Tag", back_populates="todo_tags")
  todo = relationship("Todo", back_populates="todo_tags")

  # no dupe tag on a same todo
  __table_args__ = (UniqueConstraint("todo_id", "tag_id", name="uq_todo_tag"),)


class ContactTag(Base):
  __tablename__ = "contact_tags"
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  contact_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
  )
  tag_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
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

  # includes same tags from different todos.
  tag = relationship("Tag", back_populates="contact_tags")
  contact = relationship("Contact", back_populates="contact_tags")

  # no dupe tag on a same todo
  __table_args__ = (UniqueConstraint("contact_id", "tag_id", name="uq_contact_tag"),)


class MemoTag(Base):
  __tablename__ = "memo_tags"
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  memo_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("memos.id", ondelete="CASCADE"), nullable=False
  )
  tag_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
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

  # includes same tags from different todos.
  tag = relationship("Tag", back_populates="memo_tags")
  memo = relationship("Memo", back_populates="memo_tags")

  # no dupe tag on a same todo
  __table_args__ = (UniqueConstraint("memo_id", "tag_id", name="uq_memo_tag"),)
