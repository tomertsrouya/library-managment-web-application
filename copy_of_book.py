from datetime import datetime
from Book import Book
from db_connection import db_connector
class CopyOfBook(Book):
    def __init__(self,  book_name, author, year_of_publish, publisher, branch_name, status='available'):
        # Initialize the properties of the parent class
        Book.__init__(self, book_name, author, year_of_publish, publisher)
        cursor, connection = db_connector('group31_db')
        # Get the maximum book_id from the copy_of_book table
        cursor.execute('SELECT book_ID FROM copy_of_book')
        self.status = status
        self.branch_name = branch_name
        max_book_id = cursor.fetchall()
        # Check if the table is empty or not
        if max_book_id:
            # Create a list of all book_ids and get the max value
            list_of_book_id = [int(x[0]) for x in max_book_id]
            max_book_id = max(list_of_book_id)
        else:
            max_book_id = 0
        # Increment the max value by 1 to get the new book_id
        book_id = int(max_book_id) + 1
        self.book_id = book_id
        self.arrival_date = datetime.today() # Store the current date and time as arrival date of the book.

    def insert_new_book(self, quantity):
        cursor, connect = db_connector('group31_db')
        cursor.execute(
            "INSERT INTO books_in_branches (stock_in_branch, branch_name, author_name, book_name)"
            " VALUES (%s, %s, %s, %s)",
            (quantity, self.branch_name, self.author, self.book_name)
        )
        # commit the execution
        connect.commit()
        new_copy_of_book = CopyOfBook(self.book_name, self.author, self.year_of_publish,
                                      self.publisher, self.branch_name)
        new_copy_of_book.insert_multiple_copies(quantity, cursor, connect, 0)

    def insert_copy_of_book(self, cursor, connection):
        # SQL query to insert new row into the copy_of_book table
        query = "INSERT INTO copy_of_book(book_ID, copy_of_book_status, author_name, book_name, branch_name)" \
                "VALUES(%s, %s, %s, %s, %s)"

        # Values to be inserted into the table
        val = (self.book_id,
               self.status,
               self.author,
               self.book_name,
               self.branch_name)

        # Execute the query and commit the transaction
        cursor.execute(query, val)
        connection.commit()

    def insert_multiple_copies(self, quantity, cursor, connection, stock_in_branch):
        # Check if the quantity is greater than 1
        if int(quantity) > 1:
            # Insert multiple copies
            for i in range(quantity):
                self.insert_copy_of_book(cursor, connection)
                self.book_id = self.book_id + 1
        else:
            # Insert single copy
            self.insert_copy_of_book(cursor, connection)

        # Update the stock in branch for the provided book, author and branch
        cursor.execute(
            f"UPDATE books_in_branches SET stock_in_branch = %s"
            " WHERE book_name = %s AND author_name = %s AND branch_name = %s;",
            (stock_in_branch + quantity, self.book_name, self.author, self.branch_name)
        )
        connection.commit()


