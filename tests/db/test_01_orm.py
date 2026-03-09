from sealy.db.base import Base
import sealy.db.models  # noqa


def test_tables_exist(migrated_db):
  expected_tables = {table.name for table in Base.metadata.tables.values()}
  actual = set(migrated_db.get_table_names()) - {"alembic_version"}

  missing = expected_tables - actual
  extra = actual - expected_tables
  assert not missing and not extra, (
    f"Missing tables: {', '.join(missing)}\nUnexpected tables: {', '.join(extra)}"
  )


def test_columns_exist(migrated_db):
  expected_columns = {
    table.name: {c.name for c in table.columns}
    for table in Base.metadata.tables.values()
  }

  for table, expected in expected_columns.items():
    actual_columns = {c["name"] for c in migrated_db.get_columns(table)}
    missing = expected - actual_columns
    extra = actual_columns - expected

    assert not missing and not extra, (
      f"Table: {table}\n"
      f"Missing columns: {', '.join(missing)}\n"
      f"Unexpected columns: {', '.join(extra)}"
    )


def test_column_constraints(migrated_db):
  import sqlalchemy as sa
  from sqlalchemy import UniqueConstraint
  from sqlalchemy.dialects.postgresql import ENUM as PGEnum

  for expected_table_name, expected_table in Base.metadata.tables.items():
    actual_columns = {
      c["name"]: c for c in migrated_db.get_columns(expected_table_name)
    }

    # pk
    expected_pk = {c.name for c in expected_table.primary_key.columns}
    actual_pk = set(
      migrated_db.get_pk_constraint(expected_table_name)["constrained_columns"]
    )
    assert expected_pk == actual_pk, f"PKs do not match in table {expected_table}"

    # fk, cascade, set null etc
    expected_fk = {
      (
        fk.parent.name,
        fk.column.table.name,
        fk.column.name,
        (fk.ondelete or "").lower(),
        (fk.onupdate or "").lower(),
      )
      for fk in expected_table.foreign_keys
    }
    actual_fk = {
      (
        fk["constrained_columns"][0],
        fk["referred_table"],
        fk["referred_columns"][0],
        fk.get("options", {}).get("ondelete", "").lower(),
        fk.get("options", {}).get("onupdate", "").lower(),
      )
      for fk in migrated_db.get_foreign_keys(expected_table_name)
    }
    assert actual_fk == expected_fk, f"FKs do not match in table {expected_table}"

    # unique
    expected_uniq = {
      tuple(sorted(c.name for c in uc.columns))
      for uc in expected_table.constraints
      if isinstance(uc, UniqueConstraint)
    }
    actual_uniq = {
      tuple(sorted(u["column_names"]))
      for u in migrated_db.get_unique_constraints(expected_table_name)
    }
    assert actual_uniq == expected_uniq, (
      f"Unique constraints don't match in table {expected_table}"
    )

    # Indexes
    expected_idx = {
      (tuple(idx.columns.keys()), idx.unique)
      for idx in expected_table.indexes
      # ignore unique indexes (orm unique const in fk != equal to index creation -> double counting)
      if not idx.unique
    }
    actual_idx = {
      (tuple(i["column_names"]), i["unique"])
      for i in migrated_db.get_indexes(expected_table_name)
      # here as well. it can happend in reverse!
      if not i["unique"]
    }
    assert actual_idx == expected_idx, f"Indexes don't match in table {expected_table}"

    # col types and null
    for expected_column in expected_table.columns:
      actual_column = actual_columns[expected_column.name]

      # null
      assert actual_column["nullable"] == expected_column.nullable

      # type
      actual_type = actual_column["type"]
      expected_type = expected_column.type
      # for enums
      if isinstance(actual_type, (sa.Enum, PGEnum)) and isinstance(
        expected_type, sa.Enum
      ):
        assert tuple(actual_type.enums) == tuple(expected_type.enums)
        assert actual_type.name == expected_type.name
      else:
        # compare semantic properties for enum -> meaning, loose comparison
        assert (
          actual_column["type"]._type_affinity is expected_column.type._type_affinity
        )
