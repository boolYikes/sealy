# import pytest

# from sealy.db.init_db import init_db

# @pytest.fixture
# def something(): ...


# without alembic
# def test_init_db():
#   print("yappa")
#   result = init_db()
#   assert result == 1, "something went wrong"


# with alembic
from alembic import command
from sqlalchemy import inspect


def test_migrations_create_users_table(alembic_cfg, engine):
  command.upgrade(alembic_cfg, "head")

  inspector = inspect(engine)
  assert "users" in inspector.get_table_names()


# tests:
# migrations apply cleanly,
# schema matches expectations
# upgrade/downgrade works

# tests:
# table name, columns exist, unique, nullable, indexes
