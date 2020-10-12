## About

This is meant to be a simple way to explore a postgresql/mysql database and get
data out (super light wrapper to SQLAlchemy).

Connect with DB url in the following formats:

- `postgresql://someuser:somepassword@somehost[:someport]/somedatabase`
- `mysql://someuser:somepassword@somehost[:someport]/somedatabase`

> Note: This package uses `pymysql` driver for connecting to mysql. Urls that
> start with `mysql://` will automatically be changed to use `mysql+pymysql://`.

## Install

> Ensure the `pg_config` executable is on the system

```
$ sudo apt-get install -y libpq-dev

or

$ brew install postgresql
```

Then install sql-helper

```
$ pip3 install sql-helper
```

## Usage

```
In [1]: from sql_helper import SQL

In [2]: sql = SQL('postgresql://someuser:somepassword@somehost/somedatabase')

In [3]: table_names = sql.get_tables()

In [4]: results = sql.execute('SELECT ...')
```

## Extra

### [Redshift](https://aws.amazon.com/redshift/)

Install `sqlalchemy-redshift` wherever you installed `sql-helper`

```
$ venv/bin/pip3 install sqlalchemy-redshift
```

Connect with DB url in the following format:

- `redshift+psycopg2://someuser:somepassword@somehost/somedatabase`
