# from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine

# import dotenv
import os


# PROJ_ROOT = Path(__file__).resolve().parent.parent
# dotenv.load_dotenv(os.path.join(PROJ_ROOT, ".env"))

TEST_DB_URL = os.environ.get("PG_TEST_URL", "")


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
