import click
import input_helper as ih
import sql_helper as sqh


@click.command()
@click.option(
    '--no-vi', 'no_vi', is_flag=True, default=False,
    help='Do not use vi editing mode in ipython'
)
@click.option(
    '--no-colors', 'no_colors', is_flag=True, default=False,
    help='Do not use colors / syntax highlighting in ipython'
)
@click.option(
    '--confirm-exit', 'confirm_exit', is_flag=True, default=False,
    help='Prompt "Do you really want to exit ([y]/n)?" when exiting ipython'
)
def main(**kwargs):
    """Start an ipython session with an instance of an SQL object"""
    selected = sqh.select_url_from_settings()
    if selected:
        sql = sqh.SQL(selected, attempt_docker=True, wait=True)
        ih.start_ipython(
            warn=True,
            colors=not kwargs['no_colors'],
            vi=not kwargs['no_vi'],
            confirm_exit=kwargs['confirm_exit'],
            sql=sql
        )
    else:
        print('No connection string selected')


if __name__ == '__main__':
    main()
