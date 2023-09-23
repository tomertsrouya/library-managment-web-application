"""
This is class BorrowBook, this class gathers every action to do with borrowing a book
"""
from datetime import datetime, timedelta
from help_viw_funcs import book_exists, is_book_ordered
from db_connection import db_connector


class BorrowBook:
    def __init__(self, email, book_name, author, branch_name, date_of_borrow=datetime.today()):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Set the email, date of borrow, book name, author, and branch name as attributes of the class
        self.email = email
        self.date_of_borrow = date_of_borrow
        self.book_name = book_name
        self.author = author
        self.branch_name = branch_name

        # Check if the book exists
        if book_exists(self.book_name, self.author):
            cursor.execute(f"SELECT book_id FROM copy_of_book WHERE book_name = %s and author_name = %s and "
                           f"copy_of_book_status = 'ordered by {self.email}' and branch_name = %s",
                           (self.book_name, self.author, self.branch_name))
            book_id = cursor.fetchone()
            if book_id:
                self.book_id = book_id[0]
            else:
                # Retrieve the book id of an available copy of the book
                query = "SELECT book_id FROM copy_of_book WHERE book_name = %s and author_name = %s and " \
                        "copy_of_book_status = 'available' and branch_name = %s"
                cursor.execute(query, (self.book_name, self.author, self.branch_name))

                # Fetch the retrieved book id
                book_id = cursor.fetchone()

                # If the book is available, set the book id as an attribute of the class
                if book_id is not None:
                    self.book_id = book_id[0]
                else:
                    self.book_id = None

        # Calculate the date of return as 14 days after the date of borrow and set it as an attribute of the class
        self.date_of_return = self.date_of_borrow + timedelta(days=14)

    def returning_book(self):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Retrieve the book id of the book that is being returned
        query = "SELECT book_id FROM copy_of_book WHERE book_name = %s and author_name = %s and " \
                "(copy_of_book_status = 'borrowed' OR copy_of_book_status = 'ordered') and branch_name = %s"
        cursor.execute(query, (self.book_name, self.author, self.branch_name))

        # Fetch the retrieved book id
        book_id = cursor.fetchone()

        # If the book has already been returned, flash a message
        if book_id is not None:
            self.book_id = book_id[0]
            # Check if the book is ordered and what its status is
            cursor.execute("SELECT COUNT(*) FROM book_order "
                           "WHERE book_id = %s "
                           "AND order_status = 'pending'", self.book_id)
            num_of_rows = cursor.fetchone()

            # If the book is ordered, update the order status and estimated arrival date
            if num_of_rows[0] > 0:
                cursor.execute("UPDATE book_order SET order_status = 'ordered', "
                               "estimated_arrival_date = %s WHERE book_id = %s",
                               (datetime.today().strftime('%Y-%m-%d'), self.book_id))
                cursor.execute("UPDATE copy_of_book SET copy_of_book_status = 'ordered' WHERE book_id = %s",
                               self.book_id)
                cursor.execute("SELECT email FROM book_order WHERE book_id = %s", self.book_id)
                email = cursor.fetchone()[0]
                cursor.execute(f"UPDATE copy_of_book SET copy_of_book_status = 'ordered by {email}'"
                               f"WHERE book_ID = %s",
                               self.book_id)
                connection.commit()
            else:
                cursor.execute("UPDATE copy_of_book SET copy_of_book_status = 'available' WHERE book_ID = %s",
                self.book_id)
                connection.commit()
                # Update the stock in the branch where the book was borrowed
            query = 'UPDATE books_in_branches SET stock_in_branch = stock_in_branch + 1 ' \
                    'WHERE book_name = (SELECT book_name FROM copy_of_book WHERE book_id = %s) AND ' \
                    'author_name = (SELECT author_name FROM copy_of_book WHERE book_id = %s) AND' \
                    ' branch_name = (SELECT branch_name FROM copy_of_book WHERE book_id = %s)'
            cursor.execute(query, (self.book_id, self.book_id, self.book_id))

            # Update the quantity of borrowed books for the subscriber
            cursor.execute("UPDATE subscriber SET quantity_of_borrowed_books = quantity_of_borrowed_books - 1"
                           " where email = %s", self.email)

            # Update the date of return in the borrowing table
            date_of_return = datetime.today().strftime('%Y-%m-%d')
            cursor.execute("UPDATE borrowing SET date_of_return = %s where book_id = %s",
                           (date_of_return, self.book_id))

            # Commit changes to the database and close the connection
            connection.commit()
            cursor.close()
            connection.close()
        else:
            self.book_id = book_id
        return self.book_id

    def borrow_book(self):
        cursor, connect = db_connector('group31_db')
        if self.book_id is not None:
            cursor.execute("SELECT quantity_of_borrowed_books FROM subscriber WHERE email = %s",
                           self.email)
            check = cursor.fetchone()[0]
            if check:
                quantity = check
                self.quantity = quantity + 1
            else:
                self.quantity = 1
            # create query to insert borrowing data into the table
            query1 = 'INSERT into borrowing(date_of_borrowing,book_id,date_of_return,' \
                     'extension_date_of_taking,email) values (%s,%s,%s,%s,%s)'
            # create query to update the status of the book to borrowed
            query2 = 'UPDATE copy_of_book SET copy_of_book_status = "borrowed" WHERE book_id = %s'
            # create query to update the stock in branch when the book is borrowed
            query3 = 'UPDATE books_in_branches SET stock_in_branch = stock_in_branch - 1 ' \
                     'WHERE book_name = (SELECT book_name FROM copy_of_book WHERE book_id = %s) AND ' \
                     'author_name = (SELECT author_name FROM copy_of_book WHERE book_id = %s) AND' \
                     ' branch_name = (SELECT branch_name FROM copy_of_book WHERE book_id = %s)'
            # create query to update the quantity of borrowed books by the subscriber
            query4 = 'UPDATE subscriber SET quantity_of_borrowed_books = COALESCE(quantity_of_borrowed_books, 0) + 1 ' \
                     'WHERE email = %s'
            # Check if the book is ordered
            if is_book_ordered(self.book_id):
                cursor.execute("SELECT copy_of_book_status FROM copy_of_book WHERE book_ID = %s", self.book_id)
                status = cursor.fetchone()[0]
                # Check if the borrower is the one ordered the book
                if status == f'ordered by {self.email}':
                    cursor.execute(query2, (self.book_id,))
                    cursor.execute(query3, (self.book_id, self.book_id, self.book_id))
                    cursor.execute(query4, self.email)
                    cursor.execute("UPDATE book_order SET order_status = 'borrowed' WHERE book_id = %s",
                                   (self.book_id))
                    connect.commit()
                else:
                    self.book_id = None
            else:
                cursor.execute(query2, (self.book_id,))
                cursor.execute(query3, (self.book_id, self.book_id, self.book_id))
                cursor.execute(query4, self.email)

            cursor.execute("SELECT COUNT(*) FROM borrowing WHERE email = %s and book_id = %s and date_of_borrowing = %s",
                           (self.email, self.book_id, self.date_of_borrow))
            check = cursor.fetchone()
            if check[0] == 0:
                cursor.execute(query1,
                               (self.date_of_borrow, self.book_id, self.date_of_return, None, self.email))

            # Commit changes to the database and close the connection
            connect.commit()
            cursor.close()
            connect.close()
        return self.book_id