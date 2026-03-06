from uuid import UUID as uuid
from datetime import datetime

from sqlalchemy import (
  String,
  ForeignKey,
  DateTime,
  Enum,
  Index,
  UniqueConstraint,
  func,
  text,
)
from sqlalchemy.dialects.postgresql import BOOLEAN, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sealy.db.base import Base
from sealy.db.enums import Permission


# secret = True -> cannot be shared
class Memo(Base):
  __tablename__ = "memos"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  content: Mapped[str] = mapped_column(String, nullable=False)
  note: Mapped[str] = mapped_column(String, nullable=True)
  pinned: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, server_default=text("false")
  )
  obfuscated: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, server_default=text("false")
  )
  sercret: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, server_default=text("true")
  )
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
  deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

  user = relationship("User", back_populates="memos")
  memo_tags = relationship("MemoTag", back_populates="memo")
  shared_memos = relationship("SharedMemo", back_populates="memo")


class SharedMemo(Base):
  __tablename__ = "shared_memos"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  memo_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("memos.id", ondelete="CASCADE"), nullable=False
  )
  shared_user_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
  )
  permissions: Mapped[Permission] = mapped_column(
    Enum(Permission, name="permission", values_callable=lambda e: [m.value for m in e]),
    nullable=False,
    server_default=text("'R'::permission"),
  )
  expiration: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )  # null: indefinitely
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    onupdate=func.now(),
    server_default=func.now(),
  )

  memo = relationship("Memo", back_populates="shared_memos")
  shared_user = relationship("User", back_populates="shared_memos")

  __table_args__ = (
    # the first column gets an index automatically.
    # NOTE: Index(unique=True) can do this too.
    # NOTE: But I need an index on the second column anyway.
    UniqueConstraint("memo_id", "shared_user_id", name="uq_memo_shared_user"),
    Index("idx_shared_memos_shared_user_id", "shared_user_id"),
  )
