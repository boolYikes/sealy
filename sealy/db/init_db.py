from sealy.db.base import Base
from sealy.db.session import engine

import inspect


def init_db():
  print(f"INIT_DB FROM: {inspect.getfile(init_db)}")
  print(f"engine url: {engine.url}")
  # use alembic for this. don't use this
  Base.metadata.create_all(bind=engine)
  return 1
