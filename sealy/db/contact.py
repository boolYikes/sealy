from uuid import UUID as uuid
from datetime import datetime

from sqlalchemy import (
  String,
  ForeignKey,
  DateTime,
  Enum,
  UniqueConstraint,
  Index,
  func,
  text,
)
from sqlalchemy.dialects.postgresql import BOOLEAN, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sealy.db.base import Base
from sealy.db.enums import Permission


class Contact(Base):
  __tablename__ = "contacts"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  note: Mapped[str] = mapped_column(String, nullable=True)
  pinned: Mapped[bool] = mapped_column(
    BOOLEAN, nullable=False, server_default=text("false")
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

  user = relationship("User", back_populates="contacts")
  contact_tags = relationship(
    "ContactTag", back_populates="contact", passive_deletes="all"
  )
  numbers = relationship("Number", back_populates="contact", passive_deletes="all")
  addresses = relationship("Address", back_populates="contact", passive_deletes="all")
  emails = relationship("Email", back_populates="contact", passive_deletes="all")
  shared_contacts = relationship(
    "SharedContact", back_populates="contact", passive_deletes="all"
  )


class SharedContact(Base):
  __tablename__ = "shared_contacts"

  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  contact_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
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

  contact = relationship("Contact", back_populates="shared_contacts")
  shared_user = relationship("User", back_populates="shared_contacts")

  __table_args__ = (
    # the first column gets an index automatically.
    # NOTE: Index(unique=True) can do this too.
    # NOTE: But I need an index on the second column anyway.
    UniqueConstraint("contact_id", "shared_user_id", name="uq_contact_shared_user"),
    Index("idx_shared_contacts_shared_user_id", "shared_user_id"),
  )


class Number(Base):
  __tablename__ = "numbers"
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  number: Mapped[str] = mapped_column(String(50), nullable=False)
  contact_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
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

  contact = relationship("Contact", back_populates="numbers")


class Email(Base):
  __tablename__ = "emails"
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  email: Mapped[str] = mapped_column(String(50), nullable=False)
  contact_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
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

  contact = relationship("Contact", back_populates="emails")


class Address(Base):
  __tablename__ = "addresses"
  id: Mapped[uuid] = mapped_column(
    UUID, primary_key=True, server_default=text("gen_random_uuid()")
  )
  address: Mapped[str] = mapped_column(String(255), nullable=False)
  contact_id: Mapped[uuid] = mapped_column(
    UUID, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
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

  contact = relationship("Contact", back_populates="addresses")
