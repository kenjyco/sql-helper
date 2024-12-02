## About

This is meant to be a simple way to explore a postgresql/mysql/sqlite database
and get data out (super light wrapper to SQLAlchemy).

Connect with DB url in the following formats:

- `postgresql://someuser:somepassword@somehost[:someport]/somedatabase`
- `mysql://someuser:somepassword@somehost[:someport]/somedatabase`
- `sqlite:///somedb.db`

> Note: This package uses `pymysql` driver for connecting to mysql. Urls that
> start with `mysql://` will automatically be changed to use `mysql+pymysql://`.

## Dependencies

#### pg_config for postgresql

> Ensure the `pg_config` executable is on the system

```
sudo apt-get install -y libpq-dev
```

or

```
brew install postgresql
```

#### cryptography package

If using Python 3.6, be sure to update pip to **at least version 19.3** (default pip
is 18.1) so that the pre-compiled wheel for `cryptography` can be used.
Otherwise, you will need to install the [rust compiler](https://www.rust-lang.org)
so that the `cryptography` dependency can be built
(`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y`)

## Install

```
pip3 install sql-helper
```

## Usage

```
In [1]: from sql_helper import SQL

In [2]: sql = SQL('postgresql://someuser:somepassword@somehost/somedatabase')

In [3]: table_names = sql.get_tables()

In [4]: results = sql.execute('SELECT ...')
```

## Extra

#### [Redshift](https://aws.amazon.com/redshift/)

Install `sqlalchemy-redshift` wherever you installed `sql-helper`

```
venv/bin/pip3 install sqlalchemy-redshift
```

Connect with DB url in the following format:

- `redshift+psycopg2://someuser:somepassword@somehost/somedatabase`

## Test matrix

> Tested with the following python versions and dependency combinations against
> postgres 13 and mysql 8.0 docker containers.

```
venv_py3.5.10_psycopg2-binary2.8.6_pymysql0.10.1_sqlalchemy1.3.1
venv_py3.5.10_psycopg2-binary2.8.6_pymysql0.10.1_sqlalchemy1.3.24
venv_py3.5.10_psycopg2-binary2.8.6_pymysql0.9.3_sqlalchemy1.3.1
venv_py3.5.10_psycopg2-binary2.8.6_pymysql0.9.3_sqlalchemy1.3.24
venv_py3.5.10_psycopg2-binary2.8_pymysql0.10.1_sqlalchemy1.3.1
venv_py3.5.10_psycopg2-binary2.8_pymysql0.10.1_sqlalchemy1.3.24
venv_py3.5.10_psycopg2-binary2.8_pymysql0.9.3_sqlalchemy1.3.1
venv_py3.5.10_psycopg2-binary2.8_pymysql0.9.3_sqlalchemy1.3.24

venv_py3.6.15_psycopg2-binary2.8.6_pymysql0.10.1_sqlalchemy1.3.24
venv_py3.6.15_psycopg2-binary2.8.6_pymysql0.10.1_sqlalchemy1.4.54
venv_py3.6.15_psycopg2-binary2.8.6_pymysql0.9.3_sqlalchemy1.3.24
venv_py3.6.15_psycopg2-binary2.8.6_pymysql0.9.3_sqlalchemy1.4.54
venv_py3.6.15_psycopg2-binary2.8.6_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.6.15_psycopg2-binary2.8.6_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.6.15_psycopg2-binary2.9.8_pymysql0.10.1_sqlalchemy1.3.24
venv_py3.6.15_psycopg2-binary2.9.8_pymysql0.10.1_sqlalchemy1.4.54
venv_py3.6.15_psycopg2-binary2.9.8_pymysql0.9.3_sqlalchemy1.3.24
venv_py3.6.15_psycopg2-binary2.9.8_pymysql0.9.3_sqlalchemy1.4.54
venv_py3.6.15_psycopg2-binary2.9.8_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.6.15_psycopg2-binary2.9.8_pymysql1.0.2_sqlalchemy1.4.54

venv_py3.7.17_psycopg2-binary2.9.9_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.7.17_psycopg2-binary2.9.9_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.7.17_psycopg2-binary2.9.9_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.7.17_psycopg2-binary2.9.9_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.7.17_psycopg2-binary2.9.9_pymysql1.1.1_sqlalchemy2.0.2
venv_py3.7.17_psycopg2-binary2.9.9_pymysql1.1.1_sqlalchemy2.0.36

venv_py3.8.20_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.8.20_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.8.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.8.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.8.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.2
venv_py3.8.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.36

venv_py3.9.20_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.9.20_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.9.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.9.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.9.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.2
venv_py3.9.20_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.36

venv_py3.10.15_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.10.15_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.10.15_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.10.15_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.10.15_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.2
venv_py3.10.15_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.36

venv_py3.11.10_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.11.10_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.11.10_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.11.10_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.11.10_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.2
venv_py3.11.10_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.36

venv_py3.12.7_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.12.7_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.12.7_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.12.7_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.12.7_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.2
venv_py3.12.7_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.36

venv_py3.13.0_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.3.24
venv_py3.13.0_psycopg2-binary2.9.10_pymysql1.0.2_sqlalchemy1.4.54
venv_py3.13.0_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.3.24
venv_py3.13.0_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy1.4.54
venv_py3.13.0_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.31
venv_py3.13.0_psycopg2-binary2.9.10_pymysql1.1.1_sqlalchemy2.0.36
```
