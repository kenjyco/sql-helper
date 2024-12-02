#!/usr/bin/env bash


run_cmd() {
    if [[ -z "$@" ]]; then
        echo "No python command passed in"
        return 1
    fi
	for venv_name in venv_py*; do
		echo -e "\n\n\n%%%%%%%%%%%%%%%\n  $(echo $venv_name | tr '[a-z]' '[A-Z]')\n%%%%%%%%%%%%%%%"
        echo $@
        ${venv_name}/bin/python -c "$@"
	done
}

# run_cmd "import input_helper as ih; from sqlalchemy import __version__ as sa_version; print(ih.string_to_version_tuple(sa_version))"
run_cmd "import sql_helper as sqh; print(sqh.sa_version_tuple)"
