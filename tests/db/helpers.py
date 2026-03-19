import uuid

from pytest import raises
from sqlalchemy.exc import IntegrityError

from sealy.db.enums import UserType
from sealy.db.user import User
from sealy.db.contact import Contact
from sealy.db.todo import Todo
from sealy.db.memo import Memo
from sealy.db.tag import Tag


def make_user(
  session,
  *,
  username="user",
  email=None,
  user_type=UserType.individual,
  parent=None,
  is_active=None,
  is_system=None,
  timezone_value=None,
  locale=None,
  display_name=None,
):
  user = User(
    username=username,
    email=email or f"{username}-{uuid.uuid4().hex[:8]}@example.com",
    user_type=user_type,
    parent=parent,
    timezone=timezone_value,
    locale=locale,
    display_name=display_name,
  )
  if is_active is not None:
    user.is_active = is_active
  if is_system is not None:
    user.is_system = is_system

  session.add(user)
  session.flush()
  return user


def make_todo(
  session,
  *,
  user,
  title="todo",
  priority=None,
  pinned=None,
  done=None,
  description=None,
  deadline=None,
  parent=None,
):
  todo = Todo(
    user=user,
    title=title,
    description=description,
    deadline=deadline,
    parent=parent,
  )
  if priority is not None:
    todo.priority = priority
  if pinned is not None:
    todo.pinned = pinned
  if done is not None:
    todo.done = done

  session.add(todo)
  session.flush()
  return todo


def make_tag(session, *, user, name="tag"):
  tag = Tag(user=user, name=name)
  session.add(tag)
  session.flush()
  return tag


def make_contact(session, *, user, name="contact", note=None, pinned=None):
  contact = Contact(user=user, name=name, note=note)
  if pinned is not None:
    contact.pinned = pinned
  session.add(contact)
  session.flush()
  return contact


def make_memo(
  session,
  *,
  user,
  content="memo content",
  note=None,
  pinned=None,
  obfuscated=None,
  secret=None,
):
  memo = Memo(user=user, content=content, note=note)
  if pinned is not None:
    memo.pinned = pinned
  if obfuscated is not None:
    memo.obfuscated = obfuscated
  if secret is not None:
    memo.secret = secret
  session.add(memo)
  session.flush()
  return memo


def expect_integrity_error(session):
  return raises(IntegrityError)
