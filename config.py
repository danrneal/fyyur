"""Config for SQLAlchemy and specifying db params.

Attributes:
    SECRET_KEY: A str representing a secret key used for securely signing the
        session cookie
    basedir: A str represneding the the current path
    DEBUG: A bool setting the debug config flask app config parameter
    DIALECT: A str representing the dialect of the db
    HOST: A str representing the host of the db
    PORT: An int representing the port the db is running on
    DATABASE: A str representing the db in which to connect to
    SQLALCHEMY_DATABASE_URI: A str representing the location of the db
    SQLALCHEMY_TRACK_MODIFICATIONS: A bool representing the flask app config
        parameter by the same name
"""


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
SQLALCHEMY_TRACK_MODIFICATIONS = False
