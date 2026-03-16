from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func

from sealy.db.user import User, AuthIdentity
from sealy.db.todo import Todo, TodoRecurrence, SharedTodo
from sealy.db.tag import Tag, TodoTag
from sealy.db.memo import Memo, SharedMemo
from sealy.db.contact import Contact, SharedContact, Number, Email, Address
from sealy.db.enums import UserType, Provider, Permission
from helpers import (
  make_contact,
  make_memo,
  make_tag,
  make_todo,
  make_user,
  expect_integrity_error,
)


def test_user_crud_and_defaults(session):
  user = User(
    username="alice",
    email="alice@example.com",
    user_type=UserType.individual,
  )
  session.add(user)
  session.flush()
  session.refresh(user)  # i can still roll back with this AND use validated user

  assert user.id is not None
  assert user.is_active is True
  assert user.is_system is False
  assert user.created_at is not None
  assert user.updated_at is not None
  assert user.deleted_at is None
  assert user.display_name is None
  assert user.parent_id is None

  fetched = session.get(User, user.id)
  assert fetched is not None
  assert fetched.username == "alice"
  assert fetched.email == "alice@example.com"

  fetched.display_name = "Alice"
  fetched.locale = "en-US"
  session.flush()
  session.refresh(fetched)

  assert fetched.display_name == "Alice"
  assert fetched.locale == "en-US"

  user_id = fetched.id
  session.delete(fetched)
  session.flush()

  assert session.get(User, user_id) is None


def test_user_email_unique_case_insensitive(session):
  make_user(session, username="u1", email="Case@Test.com")

  with expect_integrity_error(session):
    session.add(
      User(
        username="u2",
        email="case@test.com",
        user_type=UserType.individual,
      )
    )
    session.flush()

  session.rollback()


def test_user_parent_child_relationship_and_backref(session):
  parent = make_user(session, username="parent")
  child1 = make_user(session, username="child1", parent=parent)
  child2 = make_user(session, username="child2", parent=parent)

  session.refresh(parent)
  session.refresh(child1)
  session.refresh(child2)

  assert child1.parent == parent
  assert child2.parent == parent
  assert {c.id for c in parent.children} == {child1.id, child2.id}


def test_user_parent_fk_set_null_on_delete(session):
  parent = make_user(session, username="parent")
  child = make_user(session, username="child", parent=parent)

  session.delete(parent)
  session.flush()
  session.expire(child)
  session.refresh(child)

  assert child.parent_id is None
  assert child.parent is None


# ---------------------------
# AuthIdentity
# ---------------------------


def test_auth_identity_password_variant_valid(session):
  user = make_user(session, username="auth-user")

  auth = AuthIdentity(
    user=user,
    provider=Provider.password,
    email="login@example.com",
    password_hash="hashed-password",
    is_primary=True,
  )
  session.add(auth)
  session.flush()
  session.refresh(auth)

  assert auth.id is not None
  assert auth.user_id == user.id
  assert auth.provider == Provider.password
  assert auth.provider_user_id is None
  assert auth.is_primary is True
  assert auth.created_at is not None
  assert auth.updated_at is not None
  assert auth.user == user
  assert auth in user.auths


def test_auth_identity_oauth_variant_valid(session):
  user = make_user(session, username="oauth-user")

  auth = AuthIdentity(
    user=user,
    provider=Provider.google,
    provider_user_id="google-sub-123",
  )
  session.add(auth)
  session.flush()

  assert auth.user == user
  assert auth in user.auths


def test_auth_identity_check_constraint_rejects_incomplete_credentials(session):
  user = make_user(session, username="bad-auth")

  with expect_integrity_error(session):
    session.add(
      AuthIdentity(
        user=user,
        provider=Provider.password,
        email="only-email@example.com",
        password_hash=None,
        provider_user_id=None,
      )
    )
    session.flush()

  session.rollback()


def test_auth_identity_provider_uid_unique_when_present(session):
  user1 = make_user(session, username="u1")
  user2 = make_user(session, username="u2")

  session.add(
    AuthIdentity(
      user=user1,
      provider=Provider.google,
      provider_user_id="same-sub",
    )
  )
  session.flush()

  with expect_integrity_error(session):
    session.add(
      AuthIdentity(
        user=user2,
        provider=Provider.google,
        provider_user_id="same-sub",
      )
    )
    session.flush()

  session.rollback()


# ---------------------------
# Todo
# ---------------------------


def test_todo_crud_defaults_and_explicit_filtering(session):
  user = make_user(session, username="todo-owner")

  todo1 = make_todo(session, user=user, title="write tests")
  todo2 = make_todo(session, user=user, title="ship feature", priority=5, pinned=True)
  todo3 = make_todo(session, user=user, title="done item", done=True)

  assert todo1.priority == 0
  assert todo1.pinned is False
  assert todo1.done is False
  assert todo1.created_at is not None
  assert todo1.updated_at is not None

  pinned_titles = session.scalars(
    select(Todo.title).where(Todo.user_id == user.id, Todo.pinned.is_(True))
  ).all()
  assert pinned_titles == ["ship feature"]

  done_count = session.scalar(
    select(func.count())
    .select_from(Todo)
    .where(Todo.user_id == user.id, Todo.done.is_(True))
  )
  assert done_count == 1

  todo2.title = "ship feature v2"
  session.flush()
  session.refresh(todo2)
  assert todo2.title == "ship feature v2"

  todo3_id = todo3.id
  session.delete(todo3)
  session.flush()
  assert session.get(Todo, todo3_id) is None


def test_todo_parent_child_relationship_and_backref(session):
  user = make_user(session, username="todo-parent-owner")
  parent = make_todo(session, user=user, title="parent")
  child = make_todo(session, user=user, title="child", parent=parent)

  session.refresh(parent)
  session.refresh(child)

  assert child.parent == parent
  assert child in parent.children


def test_todo_parent_fk_set_null_on_delete(session):
  user = make_user(session, username="todo-owner")
  parent = make_todo(session, user=user, title="parent")
  child = make_todo(session, user=user, title="child", parent=parent)

  session.delete(parent)
  session.flush()
  session.refresh(child)

  assert child.parent_id is None
  assert child.parent is None


def test_todo_filter_join_and_order_by(session):
  user = make_user(session, username="todo-query-owner")
  other = make_user(session, username="other-user")

  make_todo(session, user=user, title="b task", priority=1)
  make_todo(session, user=user, title="a task", priority=10, pinned=True)
  make_todo(session, user=other, title="other task", priority=99, pinned=True)

  rows = session.execute(
    select(Todo.title, User.username)
    .join(Todo.user)
    .where(User.id == user.id)
    .order_by(Todo.priority.desc(), Todo.title.asc())
  ).all()

  assert rows == [("a task", "todo-query-owner"), ("b task", "todo-query-owner")]


# ---------------------------
# TodoRecurrence
# ---------------------------


def test_todo_recurrence_valid_non_repeating_shape(session):
  user = make_user(session, username="rec-user")
  todo = make_todo(session, user=user, title="plain todo")

  rec = TodoRecurrence(
    todo=todo,
    recurrence_type=None,
    interval=None,
    days_of_week=None,
    days_of_month=None,
    weeks_of_month=None,
    months_of_year=None,
    start_at=datetime.now(timezone.utc),
    end_at=None,
  )
  session.add(rec)
  session.flush()

  # NOTE: corrected to be a scalar values (check ORM definitions)
  assert rec.todo == todo


def test_todo_recurrence_valid_single_dimension_rule(session):
  user = make_user(session, username="rec-user-2")
  todo = make_todo(session, user=user, title="weekly todo")

  rec = TodoRecurrence(
    todo=todo,
    recurrence_type=1,
    interval=2,
    days_of_week=[1, 3, 5],
    days_of_month=None,
    weeks_of_month=None,
    months_of_year=None,
    start_at=datetime.now(timezone.utc),
    end_at=None,
  )
  session.add(rec)
  session.flush()

  assert rec.id is not None


def test_todo_recurrence_check_rejects_multiple_dimension_arrays(session):
  user = make_user(session, username="rec-bad-user")
  todo = make_todo(session, user=user, title="bad recurring todo")

  with expect_integrity_error(session):
    session.add(
      TodoRecurrence(
        todo=todo,
        recurrence_type=1,
        interval=1,
        days_of_week=[1, 2],
        days_of_month=[1, 15],
        weeks_of_month=None,
        months_of_year=None,
        start_at=datetime.now(timezone.utc),
        end_at=None,
      )
    )
    session.flush()

  session.rollback()


# ---------------------------
# Tag / TodoTag
# ---------------------------


def test_tag_crud_and_user_relationship(session):
  user = make_user(session, username="tag-owner")
  tag = make_tag(session, user=user, name="urgent")

  assert tag.user == user
  assert tag in user.tags

  tag.name = "important"
  session.flush()
  session.refresh(tag)
  assert tag.name == "important"

  tag_id = tag.id
  session.delete(tag)
  session.flush()
  assert session.get(Tag, tag_id) is None


def test_todo_tag_relationship_join_and_uniqueness(session):
  user = make_user(session, username="tag-query-owner")
  todo = make_todo(session, user=user, title="tagged todo")
  tag = make_tag(session, user=user, name="home")

  todo_tag = TodoTag(todo=todo, tag=tag)
  session.add(todo_tag)
  session.flush()

  assert todo_tag in todo.todo_tags
  assert todo_tag in tag.todo_tags
  assert todo_tag.todo == todo
  assert todo_tag.tag == tag

  rows = session.execute(
    select(Todo.title, Tag.name)
    .join(TodoTag, TodoTag.todo_id == Todo.id)
    .join(Tag, Tag.id == TodoTag.tag_id)
    .where(Todo.id == todo.id)
  ).all()

  assert rows == [("tagged todo", "home")]

  with expect_integrity_error(session):
    session.add(TodoTag(todo=todo, tag=tag))
    session.flush()

  session.rollback()


# ---------------------------
# SharedTodo
# ---------------------------


def test_shared_todo_defaults_relationship_and_uniqueness(session):
  owner = make_user(session, username="owner")
  shared_user = make_user(session, username="shared")
  todo = make_todo(session, user=owner, title="share me")

  shared = SharedTodo(todo=todo, shared_user=shared_user)
  session.add(shared)
  session.flush()
  session.refresh(shared)

  assert shared.permissions == Permission.read
  assert shared.recursive is True
  assert shared.expiration is None
  assert shared.todo == todo
  assert shared.shared_user == shared_user
  assert shared in todo.shared_todos
  assert shared in shared_user.shared_todos

  with expect_integrity_error(session):
    session.add(SharedTodo(todo=todo, shared_user=shared_user))
    session.flush()

  session.rollback()


# ---------------------------
# Memo / SharedMemo
# ---------------------------


def test_memo_crud_defaults_and_relationships(session):
  user = make_user(session, username="memo-owner")
  memo = make_memo(session, user=user, content="top secret")

  assert memo.pinned is False
  assert memo.obfuscated is False
  assert memo.secret is True
  assert memo.user == user
  assert memo in user.memos

  memo.note = "later"
  memo.obfuscated = True
  session.flush()
  session.refresh(memo)

  assert memo.note == "later"
  assert memo.obfuscated is True


def test_shared_memo_defaults_and_uniqueness(session):
  owner = make_user(session, username="memo-owner")
  shared_user = make_user(session, username="memo-shared")
  memo = make_memo(session, user=owner, content="shareable", secret=False)

  shared = SharedMemo(memo=memo, shared_user=shared_user)
  session.add(shared)
  session.flush()

  assert shared.permissions == Permission.read
  assert shared.expiration is None
  assert shared.memo == memo
  assert shared.shared_user == shared_user
  assert shared in memo.shared_memos
  assert shared in shared_user.shared_memos

  with expect_integrity_error(session):
    session.add(SharedMemo(memo=memo, shared_user=shared_user))
    session.flush()

  session.rollback()


# ---------------------------
# Contact / child rows / SharedContact
# ---------------------------


def test_contact_crud_defaults_and_relationships(session):
  user = make_user(session, username="contact-owner")
  contact = make_contact(session, user=user, name="Bob")

  assert contact.pinned is False
  assert contact.user == user
  assert contact in user.contacts

  number = Number(contact=contact, number="+82-10-1111-2222")
  email = Email(contact=contact, email="bob@example.com")
  address = Address(contact=contact, address="Seoul")
  session.add_all([number, email, address])
  session.flush()

  assert number in contact.numbers
  assert email in contact.emails
  assert address in contact.addresses
  assert number.contact == contact
  assert email.contact == contact
  assert address.contact == contact

  rows = session.execute(
    select(Contact.name, Number.number)
    .join(Number, Number.contact_id == Contact.id)
    .where(Contact.id == contact.id)
  ).all()
  assert rows == [("Bob", "+82-10-1111-2222")]


def test_shared_contact_defaults_and_uniqueness(session):
  owner = make_user(session, username="contact-owner")
  shared_user = make_user(session, username="contact-shared")
  contact = make_contact(session, user=owner, name="Alice")

  shared = SharedContact(contact=contact, shared_user=shared_user)
  session.add(shared)
  session.flush()

  assert shared.permissions == Permission.read
  assert shared.expiration is None
  assert shared.contact == contact
  assert shared.shared_user == shared_user
  assert shared in contact.shared_contacts
  assert shared in shared_user.shared_contacts

  with expect_integrity_error(session):
    session.add(SharedContact(contact=contact, shared_user=shared_user))
    session.flush()

  session.rollback()


# ---------------------------
# cascade delete checks
# ---------------------------


def test_deleting_user_cascades_owned_rows(session):
  user = make_user(session, username="cascade-owner")
  todo = make_todo(session, user=user, title="owned todo")
  tag = make_tag(session, user=user, name="owned tag")
  memo = make_memo(session, user=user, content="owned memo")
  contact = make_contact(session, user=user, name="owned contact")

  todo_id = todo.id
  tag_id = tag.id
  memo_id = memo.id
  contact_id = contact.id
  session.delete(user)
  session.flush()
  session.expire_all()

  assert session.get(Todo, todo_id) is None
  assert session.get(Tag, tag_id) is None
  assert session.get(Memo, memo_id) is None
  assert session.get(Contact, contact_id) is None


def test_deleting_todo_cascades_todo_children_tables(session):
  user = make_user(session, username="todo-cascade-owner")
  tag = make_tag(session, user=user, name="x")
  todo = make_todo(session, user=user, title="parent todo")

  todo_tag = TodoTag(todo_id=todo.id, tag_id=tag.id)
  recurrence = TodoRecurrence(
    todo_id=todo.id,
    recurrence_type=1,
    interval=1,
    days_of_week=[1],
    days_of_month=None,
    weeks_of_month=None,
    months_of_year=None,
    start_at=datetime.now(timezone.utc),
    end_at=datetime.now(timezone.utc) + timedelta(days=30),
  )
  shared = SharedTodo(
    todo_id=todo.id, shared_user_id=make_user(session, username="shared-user").id
  )

  session.add_all([todo_tag, recurrence, shared])
  session.flush()

  todo_tag_id = todo_tag.id
  recurrence_id = recurrence.id
  shared_id = shared.id

  session.delete(todo)
  session.flush()
  session.expire_all()

  assert session.get(TodoTag, todo_tag_id) is None
  assert session.get(TodoRecurrence, recurrence_id) is None
  assert session.get(SharedTodo, shared_id) is None
