def test_migrations_create_tables(migrated_db):
  tables = migrated_db.get_table_names()
  # Refactor this!!
  assert "users" in tables, "users table is not there!"
  assert "auth_identities" in tables, "auth_identities table is not there!"
  assert "todos" in tables, "todos table is not there!"
  assert "todo_recurrences" in tables, "todo_recurrences table is not there!"
  assert "contacts" in tables, "contacts table is not there!"
  assert "numbers" in tables, "numbers table is not there!"
  assert "emails" in tables, "emails table is not there!"
  assert "addresses" in tables, "addresses table is not there!"
  assert "tags" in tables, "tags table is not there!"
  assert "todo_tags" in tables, "todo_tags table is not there!"
  assert "contact_tags" in tables, "contact_tags table is not there!"
  assert "memos" in tables, "memos table is not present"
  assert "memo_tags" in tables, "memo_tags table is not present"


def test_users_table_columns(migrated_db):
  columns = {c["name"] for c in migrated_db.get_columns("users")}
  expected = {
    "id",
    "user_type",
    "parent_id",
    "username",
    "display_name",
    "email",
    "is_active",
    "is_system",
    "timezone",
    "locale",
    "created_at",
    "updated_at",
    "deleted_at",
  }
  missing = expected - columns
  assert not missing, f"Columns missing!: {missing}"


# tests:
# migrations apply cleanly,
# schema matches expectations
# upgrade/downgrade works

# tests:
# table name, columns exist, unique, nullable, indexes
