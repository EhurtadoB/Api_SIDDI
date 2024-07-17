import os

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '1804')
    MYSQL_DB = os.getenv('MYSQL_DB', 'siddi_database')
    MYSQL_CURSORCLASS = 'DictCursor'