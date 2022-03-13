import click
import input_helper as ih
import sql_helper as sqh


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
    """Start an ipython session with an instance of an SQL object"""
    selected = sqh.select_url_from_settings()
    if selected:
        sql = sqh.SQL(selected, attempt_docker=True)
        ih.start_ipython(
            warn=True,
            colors=not no_colors,
            vi=not no_vi,
            sql=sql
        )
    else:
        print('No connection string selected')


if __name__ == '__main__':
    main()
