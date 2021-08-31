import pytest

from automaps import db

def test_get_engine(monkeypatch):
    assert db.get_engine() == "1"