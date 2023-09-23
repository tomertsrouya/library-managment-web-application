"""
This is class Subscriber that lets the subscriber log in with all his details.
The details will arrive from the html, creating a subscriber.(?????) --> ask Ben10
"""
# imports
import pymysql
import pymysql as mdb
# change all mail to email
from db_connection import db_connector

class Subscriber:
    def __init__(self, first_name, last_name, email, phone_num, password,  city, street, apartment, birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.birth_date = birth_date
        self.phone_num = phone_num
        self.city = city
        self.street = street
        self.apartment = apartment
        self.password = password



    def insert_to_db(self): # change address to city stret house_num
        cursor, connect = db_connector('group31_db')

        #insert data in to suscriber table
        query = "INSERT INTO subscriber (email, first_name, last_name, city, street, house_num, phone_num, " \
                "date_of_birth, subscriber_password, quantity_of_borrowed_books)" \
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (self.email,
               self.first_name,
               self.last_name,
               self.city,
               self.street,
               self.apartment,
               self.phone_num,
               self.birth_date,
               self.password,
               0)
        try:
            cursor.execute(query, val)
            # commit the execution
            connect.commit()

            # closing the cursor ans connection
            cursor.close()
            connect.close()
        except pymysql.err.IntegrityError:
            raise 'This subscriber is already signed up'


    def borrowing_history(self): #when the days to return are finished write returned
        # Create cursor and connection
        cursor, connection = db_connector('group31_db')

        # Define the SQL query
        query = '''
            SELECT book.book_name, borrowing.date_of_borrowing, 
        CASE
            WHEN CURRENT_DATE >= borrowing.date_of_return THEN 'returned'
            WHEN CURRENT_DATE < borrowing.date_of_return THEN TIMESTAMPDIFF(day, CURRENT_DATE, borrowing.date_of_return)
        END as status
        FROM borrowing
        JOIN copy_of_book ON borrowing.book_id = copy_of_book.book_id
        JOIN book ON copy_of_book.book_name = book.book_name and copy_of_book.author_name = book.author_name
        JOIN subscriber ON borrowing.email = subscriber.email
        WHERE subscriber.email = %s

        '''

        cursor.execute(query, self.email)
        results = cursor.fetchall()

        borrowing_history = []
        for row in results:
            book_name = row[0]
            borrowing_date = row[1]
            status = row[2]
            borrowing_history.append({"book_name": book_name, "date_of_borrowing": borrowing_date, "book_status": status})

        return borrowing_history

    def order_history(self):
        # Connect to the database and create a cursor
        cursor, connect = db_connector('group31_db')
        # SQL query to retrieve order history for subscriber
        query ="""
            SELECT book.book_name, book_order.date_of_order, book_order.estimated_arrival_date, 
        DATE_ADD(book_order.estimated_arrival_date, INTERVAL 3 DAY) as last_day_reserved
        FROM book_order
        JOIN copy_of_book ON book_order.book_id = copy_of_book.book_id
        JOIN book ON copy_of_book.book_name = book.book_name and copy_of_book.author_name = book.author_name
        JOIN subscriber ON book_order.email = subscriber.email
        WHERE subscriber.email = %s 
        """
        # Execute the query with subscriber's email
        cursor.execute(query, (self.email))
        # Fetch all the results from the query
        results = cursor.fetchall()

        book_list = []
        # Iterate over the results
        for result in results:
            # Create a dictionary for each book with details
            book = {'book_name': result[0], 'order_date': result[1], 'estimated_arrival_date': result[2],
                    'arrival_plus_3': result[3]}
            # Append the dictionary to the book list
            book_list.append(book)
        # Close the cursor and connection
        cursor.close()
        connect.close()
        # Return the book list
        return book_list
