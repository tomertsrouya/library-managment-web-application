"""
This is class Worker that lets the worker log in with all his details.
The details will arrive from the html, creating a worker.(?????) --> ask Ben10
"""
import pymysql
from db_connection import db_connector


class Librarian:
    def __init__(self, first_name, last_name, email,  password, phone_num, city, street, apartment, beginning_date, branch):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone_num = phone_num
        self.city = city
        self.street = street
        self.apartment = apartment
        self.beginning_date = beginning_date
        self.branch = branch
        self.password = password


    def insert_librarian_to_db(self):
        cursor, connect = db_connector('group31_db')
        # Insert the librarian into the librarian table
        query = "INSERT INTO librarian (email, phone_num, date_of_beginning_working, city, street, house_num," \
                "first_name, last_name, branch_name, librarian_password) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (self.email,
               self.phone_num,
               self.beginning_date,
               self.city,
               self.street,
               self.apartment,
               self.first_name,
               self.last_name,
               self.branch,
               self.password)
        try:
            cursor.execute(query, val)
            # commit the execution
            connect.commit()

            # closing the cursor ans connection
            cursor.close()
            connect.close()
        except pymysql.err.IntegrityError:
            raise 'The librarian has been registered'


