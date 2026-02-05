def test_migrations_create_users_table(migrated_db):
  assert "users" in migrated_db.get_table_names(), "users table is not there!"


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
