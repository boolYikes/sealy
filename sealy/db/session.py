from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

import os
from pathlib import Path

env = os.environ.get("ENV", "dev")

if env == "dev":
  PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
  dot_env = os.path.join(PROJ_ROOT, ".env")
  load_dotenv(dot_env)

DATABASE_URL = os.environ.get("PG_URL", "")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
  bind=engine,
  autoflush=False,
  autocommit=False,
)
