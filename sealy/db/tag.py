from sqlalchemy import (
  Column,
  String,
  ForeignKey,
  UUID,
  DateTime,
  func,
  UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sealy.db.base import Base


class Tag(Base):
  __tablename__ = "tags"

  id = Column(UUID, primary_key=True)
  name = Column(String(50), nullable=False)
  user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
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

  user = relationship("User", back_populates="tags")
  todo_tags = relationship("TodoTag", back_populates="tag")
  # TODO: tags.id < memos_tags.tag_id [delete: cascade]
  # TODO: tags.id < contacts_tags.tag_id [delete: cascade]


class TodoTag(Base):
  __tablename__ = "todo_tags"
  id = Column(UUID, primary_key=True)
  todo_id = Column(UUID, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False)
  tag_id = Column(UUID, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
  created_at = Column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at = Column(
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
