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
            - postgresql://someuser:somepassword@somehost[:someport]/somedatabase
            - mysql://someuser:somepassword@somehost[:someport]/somedatabase
            - sqlite:///somedb.db
            - redshift+psycopg2://someuser:somepassword@somehost/somedatabase
                - You must install the `sqlalchemy-redshift` package wherever you
                  installed `sql-helper` to connect to a redshift instance

        Other kwargs passed in will be passed to sqlalchemy.create_engine as
        connect_args
        """
        if url.startswith('sqlite://'):
            connect_args['timeout'] = connect_timeout
        else:
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

    def _execute_raw(self, statement, params={}):
        """Pass statement to SQL engine and return object before fetchall/fetchone

        - statement: a string or path to a sql script
        - params: dict or list of dicts containing any :param names in string statement
        """
        if isfile(statement):
            with open(statement, 'r') as fp:
                script_contents = fp.read()
            with self._engine.begin() as conn:
                res = conn.execute(text(script_contents))
            return res

        with self._engine.begin() as conn:
            res = conn.execute(text(statement), params)
        return res

    def execute(self, statement, params={}):
        """Pass statement to SQL engine and return a list of dicts, or list

        - statement: a string or path to a sql script
        - params: dict or list of dicts containing any :param names in string
          statement

        If the result returns rows of info and the first result only has 1
        column, a simple list is returned; if there are multiple columns, a
        list of dicts is returned

        If the result does not return rows, or result set is empty, an empty
        list is returned
        """
        cursor = self._execute_raw(statement, params)
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

    def call_procedure(self, procedure, list_of_params=[]):
        """Call the stored procedure with specified params"""
        raw_conn = self._engine.raw_connection()
        results = None
        try:
            cursor = raw_conn.cursor()
            cursor.callproc(procedure, list_of_params)
            results = list(cursor.fetchall())
            cursor.close()
            raw_conn.commit()
        finally:
            raw_conn.close()
        return results

    def _get_postgresql_procedure_names(self, schema='', sort=False):
        if schema:
            statement = (
                "SELECT proname "
                "FROM pg_catalog.pg_namespace n "
                "JOIN pg_catalog.pg_proc p on pronamespace = n.oid "
                "WHERE nspname = '{}'".format(schema)
            )
            if sort:
                statement += " ORDER BY proname"
        else:
            statement = (
                "SELECT proname, nspname "
                "FROM pg_catalog.pg_namespace n "
                "JOIN pg_catalog.pg_proc p on pronamespace = n.oid "
                "WHERE nspname NOT IN ('pg_catalog', 'information_schema')"
            )
            if sort:
                statement += " ORDER BY nspname, proname"
        return self.execute(statement)

    def _get_mysql_procedure_names(self, sort=False):
        results = self.execute(
            "SELECT routine_name "
            "FROM information_schema.routines "
            "WHERE routine_type = 'PROCEDURE'"
        )
        if sort:
            results = sorted(results)
        return results

    def get_procedure_names(self, schema='', sort=False):
        """Return a list of procedure names

        - schema: name of schema (postgresql only)
        - sort: if True, results will be sorted by name (or by schema then name
          if postgresql and no schema specified)
        """
        if self._type == 'postgresql':
            return self._get_postgresql_procedure_names(schema=schema, sort=sort)
        elif self._type == 'mysql':
            return self._get_mysql_procedure_names(sort=sort)
        else:
            return []

    def _get_postgresql_procedure_code(self, procedure):
        return ''.join(self.execute(
            "SELECT prosrc FROM pg_proc "
            "WHERE proname = '{}'".format(procedure)
        ))

    def _get_mysql_procedure_code(self, procedure):
        return b''.join(self.execute(
            "SELECT body FROM mysql.proc "
            "WHERE name = '{}'".format(procedure)
        )).decode('utf-8')

    def get_procedure_code(self, procedure):
        """Return a string with definition of stored procedure"""
        if self._type == 'postgresql':
            return self._get_postgresql_procedure_code(procedure)
        elif self._type == 'mysql':
            return self._get_mysql_procedure_code(procedure)
        else:
            return ''

    def get_schemas(self, sort=False):
        """Return a list of schemas (postgresql only)

        - sort: if True, results will be sorted by name
        """
        results = []
        if self._type == 'postgresql':
            results = self.execute(
                "SELECT schema_name FROM information_schema.schemata"
            )
        if sort:
            results = sorted(results)
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

    def _get_postgresql_indexes(self, table, schema=None):
        if '.' in table and schema is None:
            schema, table = table.split('.', 1)
        query = (
            "SELECT * "
            "FROM pg_indexes "
            "WHERE tablename = :table "
            "ORDER BY schemaname, tablename, indexname"
        )
        results = self.execute(query, {'table': table})
        return results

    def _get_mysql_indexes(self, table):
        results = self.execute("SHOW INDEXES FROM {}".format(table))
        return results

    def get_indexes(self, table, schema=None):
        """Return a list of dicts containing info about indexes for table"""
        if self._type == 'postgresql':
            return self._get_postgresql_indexes(table, schema)
        elif self._type == 'mysql':
            return self._get_mysql_indexes(table)

    def get_columns(self, table, schema=None, name_only=False, sort=False, **kwargs):
        """Return a list of dicts containing info about columns for table

        - name_only: if True, only return the names of columns, not full dict of
          info per column
        - sort: if True, results will be sorted by name

        Additional kwargs are passed to self._inspector.get_columns
        """
        if '.' in table and schema is None:
            schema, table = table.split('.', 1)
        results = self._inspector.get_columns(table, schema=schema, **kwargs)
        if name_only:
            results = [col['name'] for col in results]
            if sort:
                results = sorted(results)
        elif sort:
            results = sorted(results, key=lambda x: x['name'])
        return results

    def get_timestamp_columns(self, table, schema=None, name_only=False,
                              sort=False, **kwargs):
        """Return a list columns that are DATE, DATETIME, TIME, or TIMESTAMP

        - name_only: if True, only return the names of columns, not full dict of
          info per column
        - sort: if True, results will be sorted by name

        Additional kwargs are passed to self.get_columns
        """
        columns = self.get_columns(table, schema=schema, **kwargs)
        results = []
        getter = lambda x: x
        sortkey = lambda x: x['name']
        if name_only:
            getter = lambda x: x['name']
            sortkey = lambda x: x
        for column in columns:
            if (
                isinstance(column['type'], sqltypes.DATE) or
                isinstance(column['type'], sqltypes.DATETIME) or
                isinstance(column['type'], sqltypes.TIME) or
                isinstance(column['type'], sqltypes.TIMESTAMP)
            ):
                results.append(getter(column))

        if sort:
            results = sorted(results, key=sortkey)
        return results

    def get_autoincrement_columns(self, table, schema=None, name_only=False,
                                  sort=False, **kwargs):
        """Return a list of dicts containing info about autoincrement columns

        - name_only: if True, only return the names of columns, not full dict of
          info per column
        - sort: if True, results will be sorted by name

        Additional kwargs are passed to self.get_columns
        """
        columns = self.get_columns(table, schema=schema, **kwargs)
        results = []
        getter = lambda x: x
        sortkey = lambda x: x['name']
        if name_only:
            getter = lambda x: x['name']
            sortkey = lambda x: x
        for column in columns:
            if column.get('autoincrement') is True:
                results.append(getter(column))

        if sort:
            results = sorted(results, key=sortkey)
        return results

    def get_required_columns(self, table, schema=None, name_only=False,
                             sort=False, **kwargs):
        """Return a list of dicts containing info about required columns

        - name_only: if True, only return the names of columns, not full dict of
          info per column
        - sort: if True, results will be sorted by name

        Additional kwargs are passed to self.get_columns
        """
        columns = self.get_columns(table, schema=schema, **kwargs)
        results = []
        getter = lambda x: x
        sortkey = lambda x: x['name']
        if name_only:
            getter = lambda x: x['name']
            sortkey = lambda x: x
        for column in columns:
            if column['nullable'] is False and column['default'] is None:
                results.append(getter(column))

        if sort:
            results = sorted(results, key=sortkey)
        return results

    def get_non_nullable_columns(self, table, schema=None, name_only=False,
                             sort=False, **kwargs):
        """Return a list of dicts containing info about non-nullable columns

        - name_only: if True, only return the names of columns, not full dict of
          info per column
        - sort: if True, results will be sorted by name

        Additional kwargs are passed to self.get_columns
        """
        columns = self.get_columns(table, schema=schema, **kwargs)
        results = []
        getter = lambda x: x
        sortkey = lambda x: x['name']
        if name_only:
            getter = lambda x: x['name']
            sortkey = lambda x: x
        for column in columns:
            if column['nullable'] is False:
                results.append(getter(column))

        if sort:
            results = sorted(results, key=sortkey)
        return results

    def insert(self, table, data):
        """Insert data to table and return generated statement

        - data: dict or list of dicts
        """
        try:
            keys = data.keys()
        except AttributeError:
            keys = data[0].keys()

        statement_start = 'insert into {} ('.format(table)
        statement_cols = ', '.join(keys) + ') values ('
        statement_vals = ', '.join([':{}'.format(k) for k in keys]) + ')'
        statement = statement_start + statement_cols + statement_vals
        self._execute_raw(statement, data)
        return statement
