import os

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'bbat5d5eu5hlaec1npct-mysql.services.clever-cloud.com')
    MYSQL_USER = os.getenv('MYSQL_USER', 'uakse15oumkncikp')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '5SHRsvCrIwzG4mQfey7n')
    MYSQL_DB = os.getenv('MYSQL_DB', 'bbat5d5eu5hlaec1npct')
    MYSQL_CURSORCLASS = 'DictCursor'