import click
import input_helper as ih
import settings_helper as sh
from sql_helper import SQL


get_setting = sh.settings_getter('sql_helper')
sql_url = get_setting('sql_url')


@click.command()
@click.option(
    '--no-colors', '-c', 'no_colors', is_flag=True, default=False,
    help='Do not use shell colors in ipython'
)
@click.option(
    '--no-vi', '-v', 'no_vi', is_flag=True, default=False,
    help='Do not use vi editing mode in ipython'
)
def main(no_colors, no_vi):
    """Start an ipython session with an instance of an SQL object for SQL_URL env var"""
    if sql_url:
        sql = SQL(sql_url)
        ih.start_ipython(
            warn=True,
            colors=not no_colors,
            vi=not no_vi,
            sql=sql,
            SQL=SQL
        )
    else:
        print('Set a connection string in the SQL_URL env var and try again')


if __name__ == '__main__':
    main()
