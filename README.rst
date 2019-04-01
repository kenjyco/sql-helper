About
-----

This is meant to be a simple way to explore a postgresql/mysql database
and get data out (super light wrapper to SQLAlchemy).

Connect with DB url in the following formats:

-  ``postgresql://someuser:somepassword@somehost/somedatabase``
-  ``mysql://someuser:somepassword@somehost/somedatabase``

..

   Note: This package uses ``pymysql`` driver for connecting to mysql.
   Urls that start with ``mysql://`` will automatically be changed to
   use ``mysql+pymysql://``.

Install
-------

::

   $ pip3 install sql-helper

Usage
-----

::

   In [1]: from sql_helper import SQL

   In [2]: sql = SQL('postgresql://someuser:somepassword@somehost/somedatabase')

   In [3]: table_names = sql.get_tables()

   In [4]: results = sql.execute('SELECT ...')
