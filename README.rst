A lightweight, transparent wrapper around SQLAlchemy (both 1.x and 2.x)
designed for interactive database exploration, debugging, testing, and
REPL-driven development workflows. Rather than building yet another ORM
or complex abstraction layer, sql-helper trusts you to understand SQL
and provides transparent, immediate access to databases with minimal
mental overhead.

It integrates seamlessly with IPython, supports automatic Docker
database provisioning, and works across SQLite, MySQL, PostgreSQL, and
Redshift with consistent APIs that adapt to database-specific behaviors.
The library also provides adaptive result formatting based on the query
structure. Single values for aggregations, simple lists for single
columns, and lists of dictionaries for multiple columns.

Tested for Python 3.6 - 3.13 using both SQLAlchemy 1.x and 2.x against
PostgreSQL 13 and MySQL 8.0 docker containers.

Connect with a DB url in the following formats:

-  ``postgresql://someuser:somepassword@somehost[:someport]/somedatabase``
-  ``mysql://someuser:somepassword@somehost[:someport]/somedatabase``

   -  *note: urls that start with ``mysql://`` will automatically be
      changed to use ``mysql+pymysql://`` since this packages uses the
      ``pymysql`` driver*

-  ``sqlite:///somedb.db``
-  ``redshift+psycopg2://someuser:somepassword@somehost/somedatabase``

   -  *note: requires separate install of the ``sqlalchemy-redshift``
      package*

Install
-------

First, ensure that the ``pg_config`` executable is on the system and
that the ``cryptography`` dependency can either be built with Rust or
the pre-compiled wheel can be used. (*See “Dependencies” section below*)

Then install with ``pip``:

::

   pip install sql-helper

Dependencies
~~~~~~~~~~~~

pg_config for postgresql
^^^^^^^^^^^^^^^^^^^^^^^^

::

   sudo apt-get install -y libpq-dev

or

::

   brew install postgresql

cryptography package
^^^^^^^^^^^^^^^^^^^^

If using Python 3.6, be sure to update pip to **at least version
20.3.4** (default pip is 18.1) so that the pre-compiled wheel for
``cryptography`` can be used. Otherwise, you will need to install the
`rust compiler <https://www.rust-lang.org>`__ so that the
``cryptography`` dependency can be built
(``curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y``)

If using Python 3.5, there is no pre-compiled wheel for ``cryptography``
(even when upgrading pip to version 20.3.4). It also cannot be built if
the rust compiler is installed. Support for Python 3.5 is effectively
removed.

pymysql package
^^^^^^^^^^^^^^^

According to https://nvd.nist.gov/vuln/detail/CVE-2024-36039, pymysql
versions below 1.1.1 are vulnerable to SQL injection. Version 1.1.1 is
only available for Python 3.7+ (final version for Python 3.6 is 1.0.2;
final working version for Python 3.5 is 0.9.3).

sqlalchemy-redshift
^^^^^^^^^^^^^^^^^^^

Only needed if connecting to `AWS
Redshift <https://aws.amazon.com/redshift/>`__

::

   pip install sqlalchemy-redshift

Configuration
-------------

sql-helper uses a settings.ini file for Docker and connection
configuration:

.. code:: ini

   [default]
   postgresql_image_version = 13-alpine
   mysql_image_version = 8.0
   postgresql_username = postgresuser
   postgresql_password = some.pass
   postgresql_db = postgresdb
   mysql_username = mysqluser
   mysql_password = some.pass
   mysql_root_password = root.pass
   mysql_db = mysqldb
   connect_timeout = 5
   sql_url =

   [dev]
   postgresql_container_name = sql-helper-postgres
   mysql_container_name = sql-helper-mysql
   postgresql_port = 5432
   mysql_port = 3306
   postgresql_rm = False
   mysql_rm = False
   postgresql_data_dir =
   mysql_data_dir =
   postgresql_url = postgresql://postgresuser:some.pass@localhost:5432/postgresdb
   mysql_url = mysql://mysqluser:some.pass@localhost:3306/mysqldb
   sqlite_url = sqlite:////tmp/some-dev.db

   [test]
   postgresql_container_name = sql-helper-postgres-test
   mysql_container_name = sql-helper-mysql-test
   postgresql_port = 5440
   mysql_port = 3310
   postgresql_rm = True
   mysql_rm = True
   postgresql_data_dir =
   mysql_data_dir =
   postgresql_url = postgresql://postgresuser:some.pass@localhost:5440/postgresdb
   mysql_url = mysql://mysqluser:some.pass@localhost:3310/mysqldb
   sqlite_url = sqlite:////tmp/some-test.db

..

   On first use, the default settings.ini file is copied to
   ``~/.config/sql-helper/settings.ini``

Use the ``APP_ENV`` environment variable to specify which section of the
``settings.ini`` file your settings will be loaded from. Any settings in
the ``default`` section can be overwritten if explicity set in another
section. If no ``APP_ENV`` is explicitly set, ``dev`` is assumed.

QuickStart
----------

.. code:: python

   import sql_helper as sqh

   # Connect to a database with automatic Docker container startup if needed
   sql = sqh.SQL('postgresql://user:pass@localhost:5432/mydb', attempt_docker=True, wait=True)

   # Execute queries with adaptive result formatting
   # Single values are returned directly
   user_count = sql.execute('SELECT count(*) FROM users')  # Returns: 42

   # Single columns become simple lists
   user_names = sql.execute('SELECT name FROM users LIMIT 3')  # Returns: ['Alice', 'Bob', 'Carol']

   # Multiple columns become lists of dictionaries
   users = sql.execute('SELECT id, name, email FROM users LIMIT 2')
   # Returns: [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}, ...]

   # Explore schema interactively
   tables = sql.get_tables()
   columns = sql.get_columns('users', name_only=True)
   timestamp_fields = sql.get_timestamp_columns('users', name_only=True)

   # Insert data with automatic parameterization
   sql.insert('users', {'name': 'David', 'email': 'david@example.com'})
   sql.insert('users', [
       {'name': 'Eve', 'email': 'eve@example.com'},
       {'name': 'Frank', 'email': 'frank@example.com'}
   ])

   # Interactive database selection (prompts user to choose from configured URLs)
   selected_url = sqh.select_url_from_settings()
   sql = sqh.SQL(selected_url, attempt_docker=True)

What you gain: **Zero-friction database exploration** with automatic
environment setup, consistent result formatting across query types, and
transparent SQL execution that you can inspect and debug. The library
eliminates the cognitive overhead of connection management, driver
selection, and result processing while preserving full control over the
actual SQL being executed.

API Overview
------------

Environment and Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``urls_from_settings()``** - Discover configured database
   connections

   -  Returns: List of all configured connection URLs from settings.ini
   -  Internal calls: None

-  **``select_url_from_settings()``** - Interactive database selection

   -  Returns: User-selected connection URL from configured options
   -  Internal calls: ``urls_from_settings()``, ``ih.make_selections()``

Docker Container Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``start_docker(db_type, exception=False, show=False, force=False, wait=True, sleeptime=2)``**
   - Launch database containers

   -  ``db_type``: ‘postgresql’ or ‘mysql’
   -  ``exception``: Raise exceptions on Docker errors
   -  ``show``: Display Docker commands and output
   -  ``force``: Stop and remove existing container before creating new
      one
   -  ``wait``: Block until database accepts connections
   -  ``sleeptime``: Seconds between connection attempts when waiting
   -  Returns: Result from Docker operation
   -  Internal calls: ``bh.tools.docker_postgres_start()``,
      ``bh.tools.docker_mysql_start()``

-  **``stop_docker(db_type, exception=False, show=False)``** - Stop
   database containers

   -  ``db_type``: ‘postgresql’ or ‘mysql’
   -  ``exception``: Raise exceptions on Docker errors
   -  ``show``: Display Docker commands and output
   -  Returns: Result from Docker operation
   -  Internal calls: ``bh.tools.docker_stop()``

Core Database Operations
~~~~~~~~~~~~~~~~~~~~~~~~

-  **``SQL(url, connect_timeout=5, attempt_docker=False, wait=False, **connect_args)``**
   - Create a database connection instance

   -  ``url``: Connection URL (postgresql://, mysql://, sqlite://,
      redshift+psycopg2://)
   -  ``connect_timeout``: Seconds to wait for connection before giving
      up
   -  ``attempt_docker``: Automatically start Docker container if
      connection fails and URL matches settings
   -  ``wait``: Block until Docker container is ready to accept
      connections
   -  ``**connect_args``: Additional arguments passed to underlying
      connection engine
   -  Returns: Configured SQL instance ready for database operations
   -  Internal calls: ``start_docker()``

-  **``SQL.execute(statement, params={})``** - Execute SQL with adaptive
   result formatting

   -  ``statement``: SQL string or path to SQL file
   -  ``params``: Dictionary or list of dictionaries for parameterized
      queries
   -  Returns: Adaptive results based on query structure: single values
      for aggregations, lists for single columns, list of dicts for
      multiple columns, single dict/value for single-row results with
      parentheses
   -  Internal calls: None

-  **``SQL.insert(table, data)``** - Insert data with automatic
   parameterization

   -  ``table``: Target table name
   -  ``data``: Dictionary (single row) or list of dictionaries
      (multiple rows)
   -  Returns: Generated INSERT statement string for debugging
   -  Internal calls: None

-  **``SQL.call_procedure(procedure, list_of_params=[])``** - Execute
   stored procedures

   -  ``procedure``: Name of stored procedure
   -  ``list_of_params``: List of parameters to pass
   -  Returns: List of results from procedure execution
   -  Internal calls: None

Schema Discovery and Introspection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``SQL.get_tables()``** - List all tables in the database

   -  Returns: List of table names (PostgreSQL returns schema.tablename
      format)
   -  Internal calls: None

-  **``SQL.get_schemas(sort=False)``** - List database schemas
   (PostgreSQL only)

   -  ``sort``: Alphabetically sort results
   -  Returns: List of schema names
   -  Internal calls: None

-  **``SQL.get_columns(table, schema=None, name_only=False, sort=False, **kwargs)``**
   - Examine table structure

   -  ``table``: Table name (supports schema.table notation for
      PostgreSQL)
   -  ``schema``: Schema name (optional, auto-detected from table if
      using dot notation)
   -  ``name_only``: Return simple list of column names instead of
      detailed dictionaries
   -  ``sort``: Alphabetically sort results
   -  ``**kwargs``: Additional arguments passed to column inspection
   -  Returns: List of column dictionaries or column names if
      name_only=True
   -  Internal calls: None

-  **``SQL.get_indexes(table, schema=None)``** - List table indexes

   -  ``table``: Table name
   -  ``schema``: Schema name (optional)
   -  Returns: List of dictionaries with index information
   -  Internal calls: None

Specialized Column Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``SQL.get_timestamp_columns(table, schema=None, name_only=False, sort=False, **kwargs)``**
   - Find date/time columns

   -  ``table``: Table name
   -  ``schema``: Schema name (optional)
   -  ``name_only``: Return simple list of column names instead of
      detailed dictionaries
   -  ``sort``: Alphabetically sort results
   -  ``**kwargs``: Additional arguments passed to column inspection
   -  Returns: Columns that are DATE, DATETIME, TIME, or TIMESTAMP types
   -  Internal calls: ``SQL.get_columns()``

-  **``SQL.get_autoincrement_columns(table, schema=None, name_only=False, sort=False, **kwargs)``**
   - Find auto-incrementing columns

   -  ``table``: Table name
   -  ``schema``: Schema name (optional)
   -  ``name_only``: Return simple list of column names instead of
      detailed dictionaries
   -  ``sort``: Alphabetically sort results
   -  ``**kwargs``: Additional arguments passed to column inspection
   -  Returns: Columns with autoincrement properties
   -  Internal calls: ``SQL.get_columns()``

-  **``SQL.get_required_columns(table, schema=None, name_only=False, sort=False, **kwargs)``**
   - Find required columns

   -  ``table``: Table name
   -  ``schema``: Schema name (optional)
   -  ``name_only``: Return simple list of column names instead of
      detailed dictionaries
   -  ``sort``: Alphabetically sort results
   -  ``**kwargs``: Additional arguments passed to column inspection
   -  Returns: Columns that are not nullable and have no default value
   -  Internal calls: ``SQL.get_columns()``

-  **``SQL.get_non_nullable_columns(table, schema=None, name_only=False, sort=False, **kwargs)``**
   - Find non-nullable columns

   -  ``table``: Table name
   -  ``schema``: Schema name (optional)
   -  ``name_only``: Return simple list of column names instead of
      detailed dictionaries
   -  ``sort``: Alphabetically sort results
   -  ``**kwargs``: Additional arguments passed to column inspection
   -  Returns: Columns that cannot contain NULL values
   -  Internal calls: ``SQL.get_columns()``

Stored Procedure Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``SQL.get_procedure_names(schema='', sort=False)``** - List stored
   procedures

   -  ``schema``: Schema name (PostgreSQL only)
   -  ``sort``: Alphabetically sort results
   -  Returns: List of procedure names
   -  Internal calls: None

-  **``SQL.get_procedure_code(procedure)``** - View procedure source
   code

   -  ``procedure``: Procedure name
   -  Returns: String containing the procedure definition
   -  Internal calls: None
