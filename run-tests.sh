#!/usr/bin/env bash

echo -e "\n\n\n\n\n\n\n\n\n"
for venv_name in venv_py*; do
# for venv_name in venv_py3.7*; do
# for venv_name in venv_py3.13*sqlalchemy2*; do
    echo -e "\n\n\n%%%%%%%%%%%%%%%\n  $(echo $venv_name | tr '[a-z]' '[A-Z]')\n%%%%%%%%%%%%%%%"
    ${venv_name}/bin/pytest
done
