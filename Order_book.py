"""
This function will find the branch that has the book they're looking for and order it.
"""
from flask import request, session, render_template, flash, redirect, url_for
from db_connection import db_connector
from datetime import datetime, timedelta
from help_viw_funcs import check_branch_name
class OrderBook:
    def __init__(self, email):
        self.date_of_order = datetime.today()
        self.email = email
        self.estimated_arrival_date = self.date_of_order + timedelta(days=14)


    def order_book(self):
        cursor, connection = db_connector('group31_db')
        branch_name = request.form['branch_name']
        book_name = request.form['book_name']
        author_name = request.form['author_name']
        email = session['email']
        result = check_branch_name(cursor, connection, branch_name)
        if result is not None:
            return 'order-book-error-branch.html'
        # Get the book_id from the copy_of_book table by joining on the book and author name
        get_book_id_query = f"SELECT copy_of_book.book_ID FROM copy_of_book JOIN book " \
                            f"ON book.book_name = copy_of_book.book_name" \
                            f" AND book.author_name = copy_of_book.author_name WHERE" \
                            f" book.book_name = %s AND book.author_name = %s " \
                            f"AND copy_of_book.branch_name = %s AND " \
                            f"copy_of_book.copy_of_book_status = 'ordered' "
        cursor.execute(get_book_id_query, (book_name, author_name, branch_name))
        result = cursor.fetchone()
        if result is None:

            # Get the book_id from the copy_of_book table by joining on the book and author name
            get_book_id_query = f"SELECT copy_of_book.book_ID FROM copy_of_book JOIN book " \
                                f"ON book.book_name = copy_of_book.book_name" \
                                f" AND book.author_name = copy_of_book.author_name WHERE" \
                                f" book.book_name = %s AND book.author_name = %s " \
                                f"AND copy_of_book.branch_name = %s AND " \
                                f"copy_of_book.copy_of_book_status = 'available' "

            cursor.execute(get_book_id_query, (book_name, author_name, branch_name))
            result = cursor.fetchone()

            if result is None:
                # Get the book_id from the copy_of_book table by joining on the book and author name
                get_book_id_query = f"SELECT copy_of_book.book_ID FROM copy_of_book " \
                                    f"JOIN book ON book.book_name = copy_of_book.book_name" \
                                f" AND book.author_name = copy_of_book.author_name " \
                                    f"JOIN borrowing ON borrowing.book_id = copy_of_book.book_id WHERE" \
                                f" book.book_name = %s AND book.author_name = %s " \
                                f"AND copy_of_book.branch_name = %s AND " \
                                f"copy_of_book.copy_of_book_status = 'borrowed' " \
                                    f"ORDER BY borrowing.date_of_borrowing ASC LIMIT 1"
                cursor.execute(get_book_id_query, (book_name, author_name, branch_name))
                result = cursor.fetchone()
                if result is None:
                    return 'order-book-rejected-not-in-stock.html'
                else:
                    book_id = result[0]
                    # Check if there is already an order for this book by another subscriber
                    check_order_query = "SELECT * FROM book_order WHERE book_id = %s " \
                                        "AND (order_status = 'ordered' OR order_status = 'pending')"
                    cursor.execute(check_order_query, book_id)
                    order_result = cursor.fetchone()
                    if order_result is None:
                        date_of_order = datetime.today()
                        cursor.execute(f"SELECT date_of_borrowing FROM borrowing "
                                       f"WHERE book_id = %s AND date_of_return > %s", (book_id, datetime.today()))
                        borrowing_result = cursor.fetchone()
                        # if borrowing_result is None:
                        #     return 'there is no book available know'
                        # else:
                        date_of_borrowing = borrowing_result[0]
                        estimated_arrival_date = date_of_borrowing + timedelta(days=14)
                        # Insert the order into the book_order table with order_status "pending"
                        insert_order_query = "INSERT INTO book_order " \
                                             "(date_of_order, order_status, email, estimated_arrival_date," \
                                             " book_id, branch_name) " \
                                             "VALUES (%s, %s, %s, %s, %s, %s)"
                        cursor.execute(insert_order_query,
                                       (date_of_order, 'pending', email, estimated_arrival_date, book_id, branch_name))
                        cursor.execute("UPDATE copy_of_book SET copy_of_book_status = 'ordered' WHERE book_id = %s",
                                       book_id)
                        connection.commit()
                        return 'order-book-approved.html'
                    else:
                        return 'order-book-rejected-ordered.html'
            else:
                return 'order-book-error.html'
        else:
            return 'order-book-rejected-ordered.html'



