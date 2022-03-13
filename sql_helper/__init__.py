import re
import bg_helper as bh
import input_helper as ih
import settings_helper as sh
from os.path import isfile
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ResourceClosedError
from sqlalchemy.sql import sqltypes
from time import sleep


SETTINGS = sh.get_all_settings(__name__).get(sh.APP_ENV, {})
CONNECT_TIMEOUT = SETTINGS.get('connect_timeout', 5)
DB_TYPES = ('postgresql', 'mysql')
rx_mysql = re.compile(r'mysql://([\S]+)')


def _settings_for_docker_ok(exception=False):
    """Return True if settings.ini has the required values set

    - exception: if True, raise an exception if settings are not ok (after
      optional sync attempt)

    If any are missing, prompt to sync settings with vimdiff
    """
    global SETTINGS
    settings_keys_for_docker = [
        'postgresql_container_name', 'postgresql_image_version', 'postgresql_username',
        'postgresql_password', 'postgresql_port', 'postgresql_db', 'postgresql_rm',
        'postgresql_data_dir', 'postgresql_url',
        'mysql_container_name', 'mysql_image_version', 'mysql_username', 'mysql_password',
        'mysql_root_password', 'mysql_port', 'mysql_db', 'mysql_rm', 'mysql_data_dir', 'mysql_url'
    ]
    missing_settings = set(settings_keys_for_docker) - set(SETTINGS.keys())
    if missing_settings != set():
        message = 'Update your settings.ini to have: {}'.format(sorted(list(missing_settings)))
        print(message)
        resp = ih.user_input('Sync settings.ini with vimdiff? (y/n)')
        if resp.lower().startswith('y'):
            sh.sync_settings_file(__name__)
            SETTINGS = sh.get_all_settings(__name__).get(sh.APP_ENV, {})
            missing_settings = set(settings_keys_for_docker) - set(SETTINGS.keys())
            if missing_settings == set():
                return True
            elif exception:
                message = 'Update your settings.ini to have: {}'.format(sorted(list(missing_settings)))
                raise Exception(message)
        else:
            if exception:
                raise Exception(message)
    else:
        return True


def start_docker(db_type, exception=False, show=False, force=False):
    """Start docker container using values from settings.ini file

    - db_type: postgresql or mysql
    - exception: if True and docker has an error response, raise an exception
    - show: if True, show the docker commands and output
    - force: if True, stop the container and remove it before re-creating
    """
    assert db_type in DB_TYPES, (
        'db_type must be one of {}... not {}'.format(
            repr(DB_TYPES), db_type
        )
    )
    ok = _settings_for_docker_ok(exception=exception)
    if not ok:
        return False

    if db_type == 'postgresql':
        return bh.tools.docker_postgres_start(
            SETTINGS['postgresql_container_name'],
            version=SETTINGS['postgresql_image_version'],
            port=SETTINGS['postgresql_port'],
            username=SETTINGS['postgresql_username'],
            password=SETTINGS['postgresql_password'],
            db=SETTINGS['postgresql_db'],
            rm=SETTINGS['postgresql_rm'],
            data_dir=SETTINGS['postgresql_data_dir'],
            exception=exception,
            show=show,
            force=force
        )
    elif db_type == 'mysql':
        return bh.tools.docker_mysql_start(
            SETTINGS['mysql_container_name'],
            version=SETTINGS['mysql_image_version'],
            port=SETTINGS['mysql_port'],
            root_password=SETTINGS['mysql_root_password'],
            username=SETTINGS['mysql_username'],
            password=SETTINGS['mysql_password'],
            db=SETTINGS['mysql_db'],
            rm=SETTINGS['mysql_rm'],
            data_dir=SETTINGS['mysql_data_dir'],
            exception=exception,
            show=show,
            force=force
        )


def stop_docker(db_type, exception=False, show=False):
    """Stop docker container for postgresql/mysql using values from settings.ini file

    - db_type: postgresql or mysql
    - exception: if True and docker has an error response, raise an exception
    - show: if True, show the docker commands and output
    """
    assert db_type in DB_TYPES, (
        'db_type must be one of {}... not {}'.format(
            repr(DB_TYPES), db_type
        )
    )
    container_key = '{}_container_name'.format(db_type)
    if container_key not in SETTINGS:
        message = 'Update your settings.ini to have: {}'.format(container_key)
        if exception is True:
            raise Exception(message)
        elif show is True:
            print(message)
        return False
    return bh.tools.docker_stop(SETTINGS[container_key], exception=exception, show=show)


def urls_from_settings():
    """Return a list of urls (connection strings) from settings.ini"""
    return [
        url
        for url in [
            SETTINGS.get('sql_url'),
            SETTINGS.get('postgresql_url'),
            SETTINGS.get('mysql_url'),
            SETTINGS.get('sqlite_url'),
        ]
        if url
    ]


def select_url_from_settings():
    """Prompt user to select a url (connection string) from settings.ini and return it"""
    urls = urls_from_settings()
    if not urls:
        print('No connection strings are defined in ~/.config/sql-helper/settings.ini')
        return
    selected = ih.make_selections(
        urls,
        prompt='Select connection string to use',
        wrap=False,
        one=True
    )
    if selected:
        return selected


class SQL(object):
    def __init__(self, url, connect_timeout=CONNECT_TIMEOUT, attempt_docker=False, **connect_args):
        """An instance that can execute SQL statements on a SQL db (postgresql/mysql/sqlite/etc)

        - url: connection url to a SQL db
            - postgresql://someuser:somepassword@somehost[:someport]/somedatabase
            - mysql://someuser:somepassword@somehost[:someport]/somedatabase
            - sqlite:///somedb.db
            - redshift+psycopg2://someuser:somepassword@somehost/somedatabase
                - You must install the `sqlalchemy-redshift` package wherever you
                  installed `sql-helper` to connect to a redshift instance
        - connect_timeout: number of seconds to wait for connection before giving up
        - attempt_docker: if True, and unable to connect initially, call start_docker
          if url matches postgresql_url or mysql_url in settings.ini

        Other kwargs passed in will be passed to sqlalchemy.create_engine as
        connect_args
        """
        if url.startswith('sqlite://'):
            connect_args['timeout'] = connect_timeout
        else:
            connect_args['connect_timeout'] = connect_timeout

        url = self._fix_mysql_url(url)
        self._engine = create_engine(url, connect_args=connect_args)
        try:
            self._inspector = inspect(self._engine)
        except OperationalError as e:
            if 'Connection refused' in repr(e) and attempt_docker is True:
                if url in [SETTINGS.get('postgresql_url'), self._fix_mysql_url(SETTINGS.get('mysql_url', ''))]:
                    if url.startswith('postgresql'):
                        db_type = 'postgresql'
                    elif url.startswith('mysql'):
                        db_type = 'mysql'
                    start_docker(db_type, show=True)
                    print('Going to sleep for 15 seconds...')
                    sleep(15)
                    self._engine = create_engine(url, connect_args=connect_args)
                    self._inspector = inspect(self._engine)
                else:
                    raise
            else:
                raise

        if (
            self._engine.url.drivername.startswith('postgresql') or
            self._engine.url.drivername == 'redshift+psycopg2'
        ):
            self._type = 'postgresql'
        elif self._engine.url.drivername.startswith('mysql'):
            self._type = 'mysql'
        elif self._engine.url.drivername.startswith('sqlite'):
            self._type = 'sqlite'
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
        """Return a list of columns that are DATE, DATETIME, TIME, or TIMESTAMP

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
