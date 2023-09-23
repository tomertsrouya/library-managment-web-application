from db_connection import db_connector
from Librarian import Librarian


def get_librarian(librarian_email, librarian_password):
    """
    This function creates a librarian object with given email and password
    :param librarian_email: str
    :param librarian_password: str
    :return: object
    """
    # Connect to the database
    cursor, connection = db_connector("group31_db")

    # Query the database for a librarian with the given email and password
    query = f"SELECT * FROM librarian WHERE email='{librarian_email}' AND librarian_password='{librarian_password}'"
    cursor.execute(query)
    librarian = cursor.fetchone()

    # If a librarian was found, create a Librarian object and return it
    if librarian:
        librarian_obj = Librarian(librarian[0], librarian[1], librarian[2], librarian[3], librarian[4], librarian[5],
                                  librarian[6], librarian[7], librarian[8], librarian[9]) # check
        return librarian_obj
    else:
        return None


def book_exists(book_name, author_name):
    """
    This function checks if the book (by book_name and author_name) exist in our data base
    :param book_name: str
    :param author_name: str
    :return: bool
    """
    # Connect to the database
    cursor, connection = db_connector('group31_db')
    # Query the database to get the num of book objects that we have with a given book name and author name
    cursor.execute("SELECT COUNT(*) from book where book_name = %s and author_name = %s",
                   (book_name, author_name))
    exists = cursor.fetchone()
    # Check if the the book exists
    if exists:
        return exists[0] > 0
    else:
        return False


def borrowing_history_helper(cursor, connection, email):
    """
    This function creates a subscriber object with a given email
    :param email: str
    :return: object
    """
    # Get subscriber object
    cursor.execute(f"SELECT * FROM subscriber WHERE email = '{email}'")
    raw_data = cursor.fetchall()[0]
    # Create a dictionary as subscriber
    data = {
        'first_name': raw_data[1],
        'last_name': raw_data[2],
        'email': raw_data[0],
        'phone_num': raw_data[6],
        'password': raw_data[8],
        'city': raw_data[3],
        'street': raw_data[4],
        'apartment': raw_data[5],
        'birth_date': raw_data[7]
    }
    cursor.close()
    connection.close()
    return data


def extension_helper(cursor, connection, email):
    """
    This function arranges the data from the data base to use in a more easy way.
    :param email: str
    :return: list
    """
    cursor.execute(
        f'''
                    SELECT book.book_name, borrowing.date_of_borrowing, copy_of_book.copy_of_book_status, borrowing.book_id, borrowing.extension_date_of_taking
                       FROM borrowing
                       JOIN copy_of_book ON borrowing.book_id = copy_of_book.book_id
                       JOIN book ON copy_of_book.book_name = book.book_name
                       WHERE borrowing.email = '{email}'

                       '''
    )
    result = cursor.fetchall()
    borrowing = []
    for row in result:
        book_name = row[0]
        borrowing_date = row[1].strftime("%Y-%m-%d")
        if row[2] == 'available':
            status = 'returned'
        else:
            status = row[2]
        book_id = row[3]
        extension_date_of_taking = row[4]
        borrowing.append(
            {'book_name': book_name, 'date_of_borrowing': borrowing_date, 'book_status': status, 'book_id': book_id,
             'extension_date_of_taking': None})
    return borrowing


def check_branch_name(cursor, connection, branch_name):
    """
    This function checks if a given branch exists
    :param branch_name: str
    :return: bool
    """
    # Query the data base to get a branch name by branch name
    cursor.execute("SELECT branch_name FROM branch WHERE branch_name = %s", branch_name)
    exist = cursor.fetchone()
    # Check if the branch exists
    if exist is None:
        return 'insert-book-error.html'
    else:
        return None


def check_less_then_three_books_borrowed(cursor, connection, email):
    """
    This function checks if a given subscriber (by email) has less then three books borrowed we can determine if
    he can borrow a book or not.
    :param email: str
    :return: bool
    """
    # Query the data base to find how many books a subscriber has
    cursor.execute(f"SELECT quantity_of_borrowed_books FROM subscriber WHERE email = '{email}'")
    num_of_book = cursor.fetchone()
    # Check if there is a subscriber as asked return True if he has less then 3 books
    if num_of_book:
        return num_of_book[0] <= 3
    else:
        return False


def check_librarian_and_book_same_branch(cursor, connection, branch, book_name, author_name):
    """
    This function check if a given book is in a given branch - the given branch is the librarians branch.
    :param branch: str
    :param book_name: str
    :param author_name: str
    :return: bool
    """
    # Query the data base get stock in branch by branch book name and author name
    cursor.execute("SELECT stock_in_branch FROM books_in_branches WHERE branch_name = %s and book_name = %s"
                   " and author_name = %s", (branch, book_name, author_name))
    stock_in_branch = cursor.fetchone()
    # Check if exists
    if stock_in_branch:
        return stock_in_branch[0] > 0
    else:
        return False

def is_book_ordered(book_id:str)->bool:
    """
    Check if a book is ordered by id in the book_order table and get the details from copy_of_book
    :param book_id: id of the book
    :return: details of the book
    """
    cursor, connection = db_connector("group31_db")
    query = f"SELECT book_order.book_id, book_order.date_of_order, book_order.estimated_arrival_date," \
            f" copy_of_book.book_name, copy_of_book.author_name  FROM book_order " \
            f"JOIN copy_of_book ON book_order.book_id = copy_of_book.book_id WHERE book_order.book_id='{book_id}'"
    cursor.execute(query)
    book_order = cursor.fetchone()
    if book_order:
        return True
