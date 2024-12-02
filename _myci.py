import os
import bg_helper as bh


# Call via the following:
#   tools-py-python ~/repos/personal/packages/sql-helper/_myci.py

this_dir = os.path.dirname(os.path.abspath(__file__))
local_package_paths = [this_dir]
# bg_helper_dir = os.path.join(os.path.dirname(this_dir), 'bg-helper')
# if os.path.isdir(bg_helper_dir):
#     local_package_paths.append(bg_helper_dir)


def create_test_environments():
    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.5.10',
        die=True,
        local_package_paths=this_dir,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '1.3.24, 1.3.1',
            'pymysql': '0.10.1, 0.9.3',
            'psycopg2-binary': '2.8.6, 2.8'
        }
    )

    # python 3.6 must have pip 19.3 or higher to use pre-compiled wheel for cryptography dep
    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.6.15',
        pip_version='19.3',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '1.4.54, 1.3.24',
            'pymysql': '1.0.2, 0.10.1, 0.9.3',
            'psycopg2-binary': '2.9.8, 2.8.6'
        }
    )

    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.7.17',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '1.4.54, 1.3.24',
            'pymysql': '1.1.1, 1.0.2',
            'psycopg2-binary': '2.9.9'
        }
    )

    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.7.17',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '2.0.36, 2.0.2',
            'pymysql': '1.1.1',
            'psycopg2-binary': '2.9.9'
        }
    )

    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.8.20, 3.9.20, 3.10.15, 3.11.10, 3.12.7, 3.13.0',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '1.4.54, 1.3.24',
            'pymysql': '1.1.1, 1.0.2',
            'psycopg2-binary': '2.9.10'
        }
    )

    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.8.20, 3.9.20, 3.10.15, 3.11.10, 3.12.7',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '2.0.36, 2.0.2',
            'pymysql': '1.1.1',
            'psycopg2-binary': '2.9.10'
        }
    )

    # sqlalchemy 2 was not supported in python 3.13 until v2.0.31
    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.13.0',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
        dep_versions_dict={
            'sqlalchemy': '2.0.36, 2.0.31',
            'pymysql': '1.1.1',
            'psycopg2-binary': '2.9.10'
        }
    )

    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.5.10, 3.7.17, 3.8.20, 3.9.20, 3.10.15, 3.11.10, 3.12.7, 3.13.0',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
    )

    bh.tools.pyenv_create_venvs_for_py_versions_and_dep_versions(
        this_dir,
        py_versions='3.6.15',
        pip_version='19.3',
        die=True,
        local_package_paths=local_package_paths,
        extra_packages='pytest<=7.4.4, pdbpp',
    )


if __name__ == '__main__':
    create_test_environments()
