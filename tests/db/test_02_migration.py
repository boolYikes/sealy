from alembic import command
import pytest

# Fixtures already run upgrades


def test_downgrade_fails(alembic_cfg):
  with pytest.raises(Exception):
    command.downgrade(alembic_cfg, "base")
