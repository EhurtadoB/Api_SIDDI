from flask_mysqldb import MySQL

def init_db(app):
    mysql = MySQL()
    app.config['MYSQL_HOST'] = app.config['MYSQL_HOST']
    app.config['MYSQL_USER'] = app.config['MYSQL_USER']
    app.config['MYSQL_PASSWORD'] = app.config['MYSQL_PASSWORD']
    app.config['MYSQL_DB'] = app.config['MYSQL_DB']
    app.config['MYSQL_CURSORCLASS'] = app.config['MYSQL_CURSORCLASS']
    mysql.init_app(app)
    return mysql