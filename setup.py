from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

setup(
    name='sql-helper',
    version='0.0.10',
    description='Helper funcs and tools for working with SQL in mysql, postgresql, and more',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/sql-helper',
    download_url='https://github.com/kenjyco/sql-helper/tarball/v0.0.10',
    packages=find_packages(),
    install_requires=[
        'PyMySQL==0.9.3',
        'SQLAlchemy==1.3.2',
        'bg-helper',
        'click>=6.0',
        'psycopg2-binary==2.8.1',
        'settings-helper',
    ],
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
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    keywords = ['sql', 'mysql', 'postgresql', 'sqlite', 'helper']
)
