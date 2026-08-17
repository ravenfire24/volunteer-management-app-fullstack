import os
from dotenv import load_dotenv


# Load env values from Backend/api/.env for local development.
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)


class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-for-volunteer-management')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql-vma-ttorta005.g.aivencloud.com')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '21957'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'avnadmin')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or os.getenv('database_password')
    MYSQL_DB = os.getenv('MYSQL_DB', 'defaultdb')
    MYSQL_SSL_CA = os.getenv('MYSQL_SSL_CA')
    MYSQL_SSL_CA_CONTENT = os.getenv('MYSQL_SSL_CA_CONTENT')

class TestConfig(Config):
    TESTING = True
    PROPAGATE_EXCEPTIONS = False
    USE_SQLITE_TEST_DB = True
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'test-secret-key-for-volunteer-suite')
    ALLOW_MISSING_EMAIL_PASSWORD = True
    MYSQL_HOST = os.getenv('TEST_MYSQL_HOST', Config.MYSQL_HOST)
    MYSQL_PORT = int(os.getenv('TEST_MYSQL_PORT', str(Config.MYSQL_PORT)))
    MYSQL_USER = os.getenv('TEST_MYSQL_USER', Config.MYSQL_USER)
    MYSQL_PASSWORD = os.getenv('TEST_MYSQL_PASSWORD') or Config.MYSQL_PASSWORD
    MYSQL_DB = os.getenv('TEST_MYSQL_DB', 'test_db')
