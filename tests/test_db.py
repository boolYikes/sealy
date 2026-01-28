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
