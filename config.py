"""Config for SQLAlchemy and specifying db params"""

import os


SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

DIALECT = 'postgresql'
USER = 'dneal'
PASS = ''
HOST = 'localhost'
PORT = 5432
DATABASE = 'fyyur'

SQLALCHEMY_DATABASE_URI = f'{DIALECT}://{USER}:{PASS}@{HOST}:{PORT}/{DATABASE}'
