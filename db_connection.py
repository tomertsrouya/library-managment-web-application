"""
This function connects to a data base with flask, with a given data base name.
"""
from flask import Flask
from flaskext.mysql import MySQL


def db_connector(db_name):
    # Setting up our application - (__name__ is referencing this file)
    app = Flask(__name__)
    # Creating an instance of the MySQL class
    mysql = MySQL()
    # Setting up configurations to form the connection:
    app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'  #host
    app.config['MYSQL_DATABASE_USER'] = 'root'  #username
    app.config['MYSQL_DATABASE_PASSWORD'] = 'root' #password
    app.config['MYSQL_DATABASE_DB'] = 'group31_db' #database name
    # Initializing the app:
    mysql.init_app(app)
    # Connect to the database
    connection = mysql.connect()
    # Create a cursor
    cursor = connection.cursor()
    # Return cursor and connection
    return cursor, connection





