import pytest
from alembic.config import Config
from sqlalchemy import create_engine

TEST_DB_URL = "postgresql+psycopg://sealy-dev:sealy-dev@localhost:5432/sealy-dev"


@pytest.fixture
def engine():
  engine = create_engine(TEST_DB_URL)
  yield engine
  engine.dispose()


@pytest.fixture
def alembic_cfg():
  cfg = Config("alembic.ini")
  cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
  return cfg
