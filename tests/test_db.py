import pytest
from sqlalchemy import text


import automaps.db


def test_db_setup(postgresql):
    cur = postgresql.cursor()
    cur.execute("SELECT id, name FROM cities")
    result = cur.fetchall()
    assert result == [(1, "Achau"), (2, "Traiskirchen")]


# def test_get_engine(mocker, postgresql):
#     engine = create_engine("postgresql+psycopg2://", creator=postgresql)
#     mocker.patch.object(automaps.db, "get_engine", return_value=engine)


def test_get_engine(mock_engine):
    engine = automaps.db.get_engine()
    result = list(engine.execute(text("SELECT id, name FROM cities")))
    assert result == [(1, "Achau"), (2, "Traiskirchen")]
