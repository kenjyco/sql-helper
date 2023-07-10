import pytest
import sql_helper as sqh


sqlite_url = sqh.SETTINGS.get('sqlite_url')
try:
    sql = sqh.SQL(sqlite_url)
    num_tables = len(sql.get_tables())
except (sqh.OperationalError, ValueError):
    sql = None
    num_tables = 0


@pytest.mark.skipif(num_tables != 0, reason='Database is not empty, has {} table(s)'.format(num_tables))
@pytest.mark.skipif(sql is None, reason='Not connected to sqlite')
@pytest.mark.skipif(not sqlite_url, reason='No sqlite_url in settings')
class TestSqlite:
    def test_empty_sqlite(self):
        assert sql._engine.url.drivername == 'sqlite'
        tables = sql.get_tables()
        assert tables == []

    def test_execute_create_table(self):
        sql.execute('create table stuff (first int, second float, third date, fourth datetime)')
        tables = sql.get_tables()
        assert tables == ['stuff']
        assert sql.get_timestamp_columns('stuff', name_only=True) == ['third', 'fourth']

    def test_columns(self):
        columns = sql.get_columns('stuff', name_only=True)
        assert columns == ['first', 'second', 'third', 'fourth']
        timestamp_columns = sql.get_timestamp_columns('stuff', name_only=True)
        assert timestamp_columns == ['third', 'fourth']

    def test_clear_db(self):
        """This MUST be the final test since it's the new teardown"""
        sql.execute('drop table stuff')
