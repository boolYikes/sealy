# TODO: Move IntEnum mapper to api side + add mapper for recurrence_type
# TODO: Enforce column level permission on admin-related elements (is_system)
# NOTE: Consider evolution strategy for zero downtime(alter table uses ACCESS EXCLUSIVE)

# TODO: Enum definitions in a separate file, denormalized tables in separate files, lookups in separate files

from sealy.db.user import User  # noqa
from sealy.db.user import AuthIdentity  # noqa
from sealy.db.todo import Todo  # noqa
from sealy.db.todo import TodoRecurrence  # noqa
from sealy.db.contact import Contact  # noqa
from sealy.db.contact import Number, Email, Address  # noqa
from sealy.db.memo import Memo  # noqa
from sealy.db.tag import Tag  # noqa
from sealy.db.tag import ContactTag, MemoTag, TodoTag  # noqa
