import re
import settings_helper as sh
from sqlalchemy import create_engine
from postgresql import PostgresqlEngine
from mysql import MysqlEngine
from sql import SQLEngine

get_setting = sh.settings_getter(__name__)
sql_url = get_setting('sql_url')
connect_timeout = get_setting('connect_timeout', 5)
rx_mysql = re.compile(r'mysql://([\S]+)')

def SQL(url, connect_timeout=connect_timeout, **connect_args):
    """An instance that can execute SQL statements on a SQL db (mysql/postgresql)

    - url: connection url to a SQL db
        - postgresql://someuser:somepassword@somehost[:someport]/somedatabase
        - mysql://someuser:somepassword@somehost[:someport]/somedatabase

    Other kwargs passed in will be passed to sqlalchemy.create_engine as
    connect_args
    """
    connect_args['connect_timeout'] = int(connect_timeout)

    """Make sure any mysql:// becomes mysql+pymysql://"""
    match = rx_mysql.match(url)
    if match:
        url = 'mysql+pymysql://' + match.group(1)

    engine = create_engine(url, connect_args=connect_args)
    if (
        engine.url.drivername.startswith('postgresql') or
        engine.url.drivername == 'redshift+psycopg2'
    ):
        return PostgresqlEngine(engine)
    elif engine.url.drivername.startswith('mysql'):
        return MysqlEngine(engine)
    else:
        return SQLEngine(engine)

