from sqlalchemy import select

from sealy.db.models import User


def test_create_records(session):
  user = User(
    user_type="individual",
    username="test_user",
    display_name="test_user_display_name",
    email="test_user_email@test.com",
    timezone="Asia/Seoul",  # TBD
    locale="ko_KR",  # TBD
  )

  session.add_all([user])
  session.commit()

  stmt = select(User).where(User.username == "test_user")
  assert session.scalar(stmt), "Row was not inserted!"

  # stmt = select(User).where(User.username.in_(["test_user"]))
  # users = list(session.scalars(stmt))
  # assert users, "Row was not inserted!"
