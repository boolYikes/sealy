# from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.engine.reflection import Inspector

# import dotenv
import os


# PROJ_ROOT = Path(__file__).resolve().parent.parent
# dotenv.load_dotenv(os.path.join(PROJ_ROOT, ".env"))

TEST_DB_URL = os.environ["PG_TEST_URL"]  # fail early
# what if I accidently use a prod db url in place of TEST_DB_URL? -> schema dropped! -> fun day at work 💀
assert any(e in TEST_DB_URL for e in ["test", "dev"]), (
  "I reserve the right to refuse turning a prod db back to the stone age"
)


@pytest.fixture(scope="session")  # set to session -> reuse, faster
def engine():
  engine = create_engine(TEST_DB_URL)
  yield engine
  engine.dispose()


@pytest.fixture
def session(engine):
  with Session(engine) as session:
    yield session
  # session = Session(engine)
  # yield session
  # session.close()


@pytest.fixture
def disposable_session(engine):
  connection = engine.connect()
  outer_transaction = connection.begin()

  # bind session to the connection
  session = Session(
    bind=connection,
    join_transaction_mode="conditional_savepoint",  # nested transactions with savepoints
  )
  try:
    yield session
  finally:
    session.close()
    outer_transaction.rollback()  # rollback everything, including nested transactions
    connection.close()  # return connection to the pool


@pytest.fixture(scope="session")
def alembic_cfg():
  cfg = Config("alembic.ini")
  cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
  return cfg


@pytest.fixture(scope="session")
def migrated_db(alembic_cfg, engine) -> Inspector:
  with engine.begin() as conn:  # clean up first
    # no accidental prod reset! this only works in psql! engine-agnositc way -> later
    dbname = conn.execute(text("select current_database()")).scalar()
    assert any(e in dbname for e in ["test", "dev"]), (
      f"Mutually assured destruction? check the db name: {dbname}"
    )
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))

  command.upgrade(alembic_cfg, "head")
  return inspect(engine)
