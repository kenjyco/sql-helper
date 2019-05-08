import re
import sqlalchemy
import settings_helper as sh
from sqlalchemy import text


get_setting = sh.settings_getter(__name__)
sql_url = get_setting('sql_url')
connect_timeout = get_setting('connect_timeout', 5)
rx_mysql = re.compile(r'mysql://([\S]+)')


class SQL(object):
    def __init__(self, url, connect_timeout=connect_timeout, **connect_args):
        """An instance that can execute SQL statements on a SQL db (mysql/postgresql)

        - url: connection url to a SQL db

        Other kwargs passed in will be passed to sqlalchemyy.create_engine as
        connect_args
        """
        connect_args['connect_timeout'] = connect_timeout
        url = self._fix_mysql_url(url)
        self._engine = sqlalchemy.create_engine(url, connect_args=connect_args)
        if self._engine.url.drivername.startswith('postgresql'):
            self._type = 'postgresql'
        elif self._engine.url.drivername.startswith('mysql'):
            self._type = 'mysql'
        else:
            self._type = self._engine.url.drivername

    def _fix_mysql_url(self, url):
        """Make sure any mysql:// becomes mysql+pymysql://"""
        match = rx_mysql.match(url)
        if match:
            url = 'mysql+pymysql://' + match.group(1)
        return url

    def _execute_raw(self, query):
        """Pass query to SQL engine and return object before fetchall/fetchone"""
        return self._engine.execute(text(query))

    def execute(self, query):
        """Pass query to SQL engine and return a list of dicts, list, or empty list

        If first result from query only has 1 column, a simple list is returned;
        if there are multiple columns, a list of dicts is returned
        """
        cursor = self._execute_raw(query)
        results = []
        first = cursor.fetchone()
        others = cursor.fetchall()
        num_columns = len(first)
        if num_columns == 1:
            results.append(first[0])
            results.extend([row[0] for row in others])
        elif num_columns > 1:
            results.append(dict(first.items()))
            results.extend([dict(row.items()) for row in others])
        return results

    def _get_postgresql_tables(self):
        results = self.execute(
            "SELECT schemaname, tablename "
            "FROM pg_catalog.pg_tables "
            "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema' "
            "ORDER BY schemaname, tablename"
        )
        return [
            r['schemaname'] + '.' + r['tablename']
            for r in results
        ]

    def _get_mysql_tables(self):
        results = self._execute_raw("show tables")
        return [r[0] for r in results.fetchall()]

    def get_tables(self):
        """Return a list of table names (or schema.tablename strings)"""
        if self._type == 'postgresql':
            return self._get_postgresql_tables()
        elif self._type == 'mysql':
            return self._get_mysql_tables()
