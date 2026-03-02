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
  contact_tags = relationship("ContactTag", back_populates="tag")
  numbers = relationship("Number", back_populates="contact")
  addresses = relationship("Address", back_populates="contact")
  emails = relationship("Email", back_populates="contact")


# TODO: Ref: contacts.id < shared_contacts.contact_id [delete: cascade]


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
