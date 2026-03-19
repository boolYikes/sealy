from sqlalchemy import select
from sealy.db.user import User
from sealy.db.todo import Todo
from helpers import (
  make_user,
  make_todo,
)


def test_rollback_reverts_flushed_changes_in_queries(session):
  """Verify that rollback reverts flushed changes for subsequent queries"""
  user = make_user(session, username="user-query", display_name="Old Name")
  session.commit()  # otherwise queried will get none
  # Flush a change
  user.display_name = "Updated Name"
  session.flush()

  # Verify the change was flushed
  assert user.display_name == "Updated Name"

  # Rollback the flush
  session.rollback()

  # Query should see the original value (not in-memory change)
  queried = session.scalar(select(User).where(User.id == user.id))
  assert queried.display_name == "Old Name"


def test_flush_visibility_in_session(session):
  """Verify that flushed changes are visible within the session"""
  user = make_user(session, username="flush-user")

  # Make and flush changes
  user.display_name = "Flushed Name"
  session.flush()

  # Changes should be visible in session immediately
  assert user.display_name == "Flushed Name"

  # Query should also see flushed changes
  queried = session.scalar(select(User).where(User.id == user.id))
  assert queried is user
  assert queried.display_name == "Flushed Name"


def test_explicit_rollback_discards_new_objects(session):
  """Verify that explicit rollback removes newly added objects from session"""
  user = make_user(session, username="todo-owner")

  # Add a new todo but don't commit
  todo = Todo(user=user, title="uncommitted todo")
  session.add(todo)
  session.flush()

  # Capture the ID
  todo_id = todo.id

  # Verify it's in session before rollback
  queried = session.get(Todo, todo_id)
  assert queried is not None
  assert queried.title == "uncommitted todo"

  # Rollback
  session.rollback()

  # After rollback, new object is expunged from session
  assert session.get(Todo, todo_id) is None


def test_atomic_multi_step_operations_all_created(session):
  """Verify that multi-step operations create all objects atomically"""
  user1 = make_user(session, username="atomic-user1")
  user2 = make_user(session, username="atomic-user2")

  # Create multiple related objects
  todo1 = make_todo(session, user=user1, title="step 1")
  todo2 = make_todo(session, user=user1, title="step 2", parent=todo1)
  todo3 = make_todo(session, user=user2, title="step 3")

  # Verify all were created with proper relationships
  assert todo1.id is not None
  assert todo2.parent_id == todo1.id
  assert todo3.parent_id is None


def test_session_identity_map_returns_same_object(session):
  """Verify session identity map ensures single instance per primary key"""
  user = make_user(session, username="identity-user")
  user_id = user.id

  # Modify the object
  user.display_name = "Changed Name"
  session.flush()

  # Query for it should return the exact same object
  queried = session.get(User, user_id)
  assert queried is user  # Same object in memory
  assert queried.display_name == "Changed Name"

  # Changes are visible
  assert user.display_name == "Changed Name"


def test_session_state_persists_through_queries(session):
  """Verify session state persists and is visible through queries"""
  user = make_user(session, username="query-user")

  # Create and modify todo in one transaction
  todo1 = Todo(user=user, title="initial todo")
  session.add(todo1)
  session.flush()

  todo1_id = todo1.id

  # Modify it
  todo1.title = "modified title"
  session.flush()

  # Query for the modified title - it should be visible
  todos = session.scalars(select(Todo).where(Todo.title == "modified title")).all()
  assert len(todos) == 1
  assert todos[0].id == todo1_id

  # Original title query returns nothing
  todos_original = session.scalars(
    select(Todo).where(Todo.title == "initial todo")
  ).all()
  assert len(todos_original) == 0


def test_multiple_users_in_session(session):
  """Verify multiple objects can be tracked in the same session"""
  user1 = make_user(session, username="alice")
  user2 = make_user(session, username="bob")
  user3 = make_user(session, username="charlie")

  # All should be in session
  assert session.get(User, user1.id) is user1
  assert session.get(User, user2.id) is user2
  assert session.get(User, user3.id) is user3

  # Modifications to one don't affect others
  user1.display_name = "Alice Updated"
  session.flush()

  assert user1.display_name == "Alice Updated"
  assert user2.display_name is None
  assert user3.display_name is None
