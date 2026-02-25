from uuid import UUID as uuid
from datetime import datetime

from sqlalchemy import (
  String,
  ForeignKey,
  DateTime,
  func,
  text,
)
from sqlalchemy.dialects.postgresql import BOOLEAN, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sealy.db.base import Base


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


# TODO: memos.id < shared_memos.memo_id [delete: cascade]
