from sealy.db.base import Base
from sealy.db.session import engine


# use alembic for this. don't use as is
def init_db():
  Base.metadata.create_all(bind=engine)
