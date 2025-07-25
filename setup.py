from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

with open('requirements.txt', 'r') as fp:
    requirements = [req for req in fp.read().splitlines() if req and not req.startswith('#')]

setup(
    name='sql-helper',
    version='0.1.0',
    description='Helper funcs and tools for working with SQL in mysql, postgresql, and more',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/sql-helper',
    download_url='https://github.com/kenjyco/sql-helper/tarball/v0.1.0',
    packages=find_packages(),
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
    install_requires=requirements,
    include_package_data=True,
    package_dir={'': '.'},
    package_data={
        '': ['*.ini'],
    },
    entry_points={
        'console_scripts': [
            'sql-ipython=sql_helper.scripts.sql_ipython:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    keywords=['sql', 'data', 'database', 'cli', 'command-line', 'sqlalchemy', 'mysql', 'postgresql', 'sqlite', 'helper', 'kenjyco']
)
