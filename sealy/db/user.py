from uuid import UUID as uuid
from datetime import datetime

from sqlalchemy import (
  String,
  Enum,
  ForeignKey,
  DateTime,
  func,
  CheckConstraint,
  Index,
  text,
)
from sqlalchemy.dialects.postgresql import CITEXT, BOOLEAN, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sealy.db.base import Base
from sealy.db.enums import UserType, Provider


class User(Base):
  __tablename__ = "users"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  user_type: Mapped[UserType] = mapped_column(
    Enum(UserType, name="user_type"), nullable=False
  )
  parent_id: Mapped[uuid | None] = mapped_column(
    UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
  )
  username: Mapped[str] = mapped_column(String, nullable=False)
  display_name: Mapped[str | None] = mapped_column(
    String, nullable=True
  )  # i dunno. redundant?!
  email: Mapped[str] = mapped_column(CITEXT, unique=True, index=True)
  is_active: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, server_default=text("true")
  )
  is_system: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, server_default=text("false")
  )
  timezone: Mapped[str] = mapped_column(String, nullable=True)
  locale: Mapped[str] = mapped_column(String, nullable=True)
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
  contacts = relationship("Contact", back_populates="user")
  memos = relationship("Memo", back_populates="user")
  shared_todos = relationship("SharedTodo", back_populates="shared_user")


class AuthIdentity(Base):
  __tablename__ = "auth_identities"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  user_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
  )
  provider: Mapped[Provider] = mapped_column(
    Enum(Provider, name="provider"), nullable=False
  )
  provider_user_id: Mapped[str | None] = mapped_column(String, nullable=True)
  password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
  email: Mapped[str | None] = mapped_column(CITEXT, nullable=True)
  is_primary: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, default=False, server_default=text("false")
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
