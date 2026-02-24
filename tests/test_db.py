def test_migrations_create_tables(migrated_db):
  assert "users" in migrated_db.get_table_names(), "users table is not there!"
  assert "auth_identities" in migrated_db.get_table_names(), (
    "auth_identities table is not there!"
  )
  assert "todos" in migrated_db.get_table_names(), "todos table is not there!"
  assert "todo_recurrences" in migrated_db.get_table_names(), (
    "todo_recurrences table is not there!"
  )
  assert "contacts" in migrated_db.get_table_names(), "contacts table is not there!"
  assert "numbers" in migrated_db.get_table_names(), "numbers table is not there!"
  assert "emails" in migrated_db.get_table_names(), "emails table is not there!"
  assert "addresses" in migrated_db.get_table_names(), "addresses table is not there!"
  assert "tags" in migrated_db.get_table_names(), "tags table is not there!"
  assert "todo_tags" in migrated_db.get_table_names(), "todo_tags table is not there!"
  assert "contact_tags" in migrated_db.get_table_names(), (
    "contact_tags table is not there!"
  )


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
