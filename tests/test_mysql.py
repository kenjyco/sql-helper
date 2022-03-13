import pytest
import sql_helper as sqh


mysql_url = sqh.SETTINGS.get('mysql_url')
try:
    sql = sqh.SQL(mysql_url, attempt_docker=True)
    num_tables = len(sql.get_tables())
except:
    sql = None
    num_tables = 0


@pytest.mark.skipif(num_tables != 0, reason='Database is not empty, has {} table(s)'.format(num_tables))
@pytest.mark.skipif(sql is None, reason='Not connected to mysql')
class TestMysql:
    def test_empty_mysql(self):
        assert sql._engine.url.drivername == 'mysql+pymysql'
        tables = sql.get_tables()
        assert tables == []

    def test_execute_create_table(self):
        sql.execute('create table stuff (first int, second float, third date)')
        tables = sql.get_tables()
        assert tables == ['stuff']

    def test_columns(self):
        columns = sql.get_columns('stuff', name_only=True)
        assert columns == ['first', 'second', 'third']
        timestamp_columns = sql.get_timestamp_columns('stuff', name_only=True)
        assert timestamp_columns == ['third']

    def test_clear_db(self):
        """This MUST be the final test since it's the new teardown"""
        sql.execute('drop table stuff')
        # sqh.stop_docker('mysql')
