import pytest
import sql_helper as sqh
from datetime import date, datetime
from decimal import Decimal


mysql_url = sqh.SETTINGS.get('mysql_url')
try:
    sql = sqh.SQL(mysql_url, attempt_docker=True, wait=True)
    num_tables = len(sql.get_tables())
except (sqh.OperationalError, ValueError):
    sql = None
    num_tables = 0


@pytest.mark.skipif(num_tables != 0, reason='Database is not empty, has {} table(s)'.format(num_tables))
@pytest.mark.skipif(sql is None, reason='Not connected to mysql')
@pytest.mark.skipif(not mysql_url, reason='No mysql_url in settings')
class TestMysql:
    def test_empty_mysql(self):
        assert sql._engine.url.drivername == 'mysql+pymysql'
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

    def test_insert_one(self):
        statement = sql.insert('stuff', {'first': 5, 'second': 1.23, 'third': '2022-05-05', 'fourth': '2022-05-05 09:30:10'})
        assert statement == 'insert into stuff (first, second, third, fourth) values (:first, :second, :third, :fourth)'
        assert sql.execute('select first from stuff') == [5]
        assert sql.execute('select count(*) from stuff') == 1
        statement2 = sql.insert('stuff', {'first': 10})
        assert statement2 == 'insert into stuff (first) values (:first)'
        assert sql.execute('select first from stuff') == [5, 10]
        assert sql.execute('select second from stuff') == [1.23, None]
        assert sql.execute('select count(*) from stuff') == 2

    def test_insert_many(self):
        data = [
            {'first': -1, 'second': 1.23, 'third': '2022-05-05', 'fourth': '2022-05-05 09:30:10'},
            {'first': 7, 'second': 1.23, 'third': '2022-05-05', 'fourth': '2022-05-05 09:30:10'},
            {'first': 25, 'second': 1.23, 'third': '2022-05-05', 'fourth': '2022-05-05 09:30:10'},
            {'first': 20, 'second': 1.23, 'third': '2022-05-05', 'fourth': '2022-05-05 09:30:10'},
            {'first': -10, 'second': 1.23, 'third': '2022-05-10', 'fourth': '2022-05-10 09:30:10'},
        ]
        statement = sql.insert('stuff', data)
        assert statement == 'insert into stuff (first, second, third, fourth) values (:first, :second, :third, :fourth)'
        nums = sql.execute('select first from stuff')
        assert nums == [5, 10, -1, 7, 25, 20, -10]
        assert sum(nums) == 56
        assert sql.execute("select sum(first) from stuff") == Decimal('56')
        results = sql.execute("select * from stuff where fourth > '2022-05-07'")
        assert len(results) == 1
        assert type(results) == list
        assert type(results[0]) == dict
        assert type(results[0]['fourth']) == datetime
        assert type(results[0]['third']) == date
        results2 = sql.execute("select fourth from stuff where fourth > '2022-05-07'")
        assert len(results2) == 1
        assert type(results2) == list
        assert type(results2[0]) == datetime
        results3 = sql.execute("select max(fourth) from stuff where fourth > '2022-05-07'")
        assert type(results3) == datetime

    def test_clear_db(self):
        """This MUST be the final test since it's the new teardown"""
        sql.execute('drop table stuff')
        # sqh.stop_docker('mysql')
