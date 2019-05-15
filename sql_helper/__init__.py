import re
import settings_helper as sh
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.sql import sqltypes
from os.path import isfile


get_setting = sh.settings_getter(__name__)
sql_url = get_setting('sql_url')
connect_timeout = get_setting('connect_timeout', 5)
rx_mysql = re.compile(r'mysql://([\S]+)')


class SQL(object):
    def __init__(self, url, connect_timeout=connect_timeout, **connect_args):
        """An instance that can execute SQL statements on a SQL db (mysql/postgresql)

        - url: connection url to a SQL db

        Other kwargs passed in will be passed to sqlalchemy.create_engine as
        connect_args
        """
        connect_args['connect_timeout'] = connect_timeout
        url = self._fix_mysql_url(url)
        self._engine = create_engine(url, connect_args=connect_args)
        self._inspector = inspect(self._engine)
        if (
            self._engine.url.drivername.startswith('postgresql') or
            self._engine.url.drivername == 'redshift+psycopg2'
        ):
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
        """Pass query to SQL engine and return object before fetchall/fetchone

        - query: a string or path to a sql script
        """
        if isfile(query):
            with open(query, 'r') as fp:
                script_contents = fp.read()
            with self._engine.begin() as conn:
                res = conn.execute(text(script_contents))
            return res
        return self._engine.execute(text(query))

    def execute(self, query):
        """Pass query to SQL engine and return a list of dicts, list, or empty list

        - query: a string or path to a sql script

        If first result from query only has 1 column, a simple list is returned;
        if there are multiple columns, a list of dicts is returned
        """
        cursor = self._execute_raw(query)
        results = []
        try:
            first = cursor.fetchone()
        except ResourceClosedError as err:
            if 'result object does not return rows' in repr(err):
                return results
            else:
                raise
        if first is None:
            return results

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
        return self.execute("show tables")

    def get_tables(self):
        """Return a list of table names (or schema.tablename strings)"""
        if self._type == 'postgresql':
            return self._get_postgresql_tables()
        elif self._type == 'mysql':
            return self._get_mysql_tables()
        else:
            return self._engine.table_names()

    def get_columns(self, table, schema=None, **kwargs):
        """Return a list of dicts containing info about columns for table

        Additional kwargs are passed to self._inspector.get_columns
        """
        if '.' in table and schema is None:
            schema, table = table.split('.', 1)
        return self._inspector.get_columns(table, schema=schema, **kwargs)

    def get_indexes(self, table, schema=None, **kwargs):
        """Return a list of dicts containing info about indexes for table

        Additional kwargs are passed to self._inspector.get_indexes
        """
        if '.' in table and schema is None:
            schema, table = table.split('.', 1)
        return self._inspector.get_indexes(table, schema=schema, **kwargs)

    def get_timestamp_columns(self, table, schema=None, name_only=False, **kwargs):
        """Return a list columns that are DATE, DATETIME, TIME, or TIMESTAMP

        - name_only: if True, only return the names of columns, not full dict of
          info per column

        Additional args/kwargs are passed to self.get_columns
        """
        columns = self.get_columns(table, schema=schema, **kwargs)
        results = []
        getter = lambda x: x
        if name_only:
            getter = lambda x: x['name']
        for column in columns:
            if (
                isinstance(column['type'], sqltypes.DATE) or
                isinstance(column['type'], sqltypes.DATETIME) or
                isinstance(column['type'], sqltypes.TIME) or
                isinstance(column['type'], sqltypes.TIMESTAMP)
            ):
                results.append(getter(column))

        return results
