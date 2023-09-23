from db_connection import db_connector
from datetime import datetime


class Borrows:
    def __init__(self, email, book_id):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Set the book_id as an attribute of the class
        self.book_id = book_id

        # Retrieve information from the database about the borrowing associated with the given email and book_id
        cursor.execute(f"select * from borrowing where email = '{email}' and book_id = '{self.book_id}'")

        # Unpack the retrieved information and assign it to class attributes
        self.date_of_borrowing, self.book_id, self.date_of_return, self.extension_date_of_taking, self.email, \
            = cursor.fetchall()[0]

    def borrowing_history(self):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Retrieve information about the borrowing history of the book with the given book_id
        cursor.execute(f"SELECT b.book_name, b.author_name, bi.branch_name, bi.stock_in_branch "
                       f"FROM borrowing bo JOIN copy_of_book c ON c.book_id = bo.book_id"
                       f" JOIN books_in_branches bi ON bi.book_name = c.book_name AND"
                       f" bi.author_name = c.author_name AND bi.branch_name = c.branch_name"
                       f"WHERE bo.book_id = %s;", self.book_id)

        # Fetch the retrieved information
        data_as_tuple = cursor.fetchall()

        # Return the retrieved information as a tuple
        return data_as_tuple

    def extension(self, new_date):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Retrieve the number of pending orders for the book
        cursor.execute(
            f'''
                            SELECT COUNT(*)
                            FROM book_order
                            WHERE book_id = '{self.book_id}' 
                            AND (order_status = 'ordered' OR order_status = 'pending')
                            '''
        )

        # Fetch the number of pending orders
        num_of_orders = cursor.fetchone()

        # If there are pending orders, return 'extension_rejected'
        if num_of_orders[0] > 0:
            return 'extension_rejected'

        # If there are no pending orders, update the borrowing information in the database
        cursor.execute("UPDATE borrowing SET extension_date_of_taking = %s, date_of_return = %s"
                       "WHERE book_id = %s",
                       (datetime.today().date(), new_date, self.book_id))

        # Commit the changes to the database
        connection.commit()
        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Return 'extension_approved'
        return 'extension_approved'



    def borrowing_doc(self, book_name, author_name, branch_name):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Retrieve the stock count of the book from the database
        cursor.execute("SELECT stock_in_branch FROM books_in_branches WHERE book_name = %s and author_name = %s"
                       " and branch_name = %s",
                       (book_name, author_name, branch_name))

        # Fetch the stock count
        stock_counter = cursor.fetchone()[0]

        # Return the stock count
        return stock_counter




