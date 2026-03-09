from alembic import command
import pytest


def test_downgrade_fails(alembic_cfg):
  with pytest.raises(Exception):
    command.downgrade(alembic_cfg, "base")
