import secrets
import time
from Order_book import OrderBook
from Subscriber import Subscriber
from flask import Flask, redirect, request, render_template, session
from flask_session import Session
from db_connection import db_connector
from datetime import datetime
from Branch import Branch
from Librarian import Librarian
from copy_of_book import CopyOfBook
from Borrow_book import BorrowBook
from borrows import Borrows
from search import search_view_func_helper
from help_viw_funcs import book_exists, borrowing_history_helper, extension_helper, check_branch_name, \
    check_less_then_three_books_borrowed, check_librarian_and_book_same_branch
from datetime import timedelta

app = Flask(__name__)

secret_key = secrets.token_hex(16)
print(secret_key)
app.secret_key = secret_key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def homepage_not_logged():
    return render_template('homepage-not-logged.html')


@app.route('/log-in', methods=['GET', 'POST'])
def redirect_sign_up():
    cursor, connection = db_connector('group31_db')
    if request.method == 'POST':
        # check if the user is trying to log in or sign up
        if 'login' in request.form:
            # get the email and password entered by the user
            email = request.form['email']
            password = request.form['password']
            # check the email and password against the database
            cursor.execute("SELECT * FROM subscriber WHERE email = %s and subscriber_password = %s", (email, password))
            subscriber = cursor.fetchone()
            cursor.execute("SELECT * FROM librarian WHERE email = %s and librarian_password = %s", (email, password))
            librarian = cursor.fetchone()
            if subscriber:
                # store the email in the session
                session['email'] = email
                # redirect to the appropriate home page
                return render_template('homepage-subscriber.html')
            elif librarian:
                # store the email in the session
                session['email'] = email
                cursor.execute("SELECT branch_name FROM librarian WHERE email = %s", session['email'])
                session['branch'] = cursor.fetchone()[0]
                # redirect to the appropriate home page
                return render_template('homepage-librarian.html')
            else:
                return render_template('log-in-error.html')
        elif 'sign_up' in request.form:
            # define the val that is selected by the radio button
            role = request.form['role']
            if role == 'librarian':
                cursor, connect = db_connector('group31_db')
                query = "SELECT branch_name FROM branch"
                cursor.execute(query)
                branches = cursor.fetchall()
                cursor.close()
                connect.close()
                return render_template('sign-up-librarian.html', branches=branches)
            elif role == 'subscriber':
                return render_template('sign-up-subscriber.html')
    return render_template('log-in.html')


############################################# not logged ###############################################################
@app.route('/new-arrivals-not-logged')
def new_arrivals():
    cursor, connect = db_connector('group31_db')
    query = """
        SELECT *
        FROM book
        WHERE cover_photo IS NOT NULL AND book_description IS NOT NULL
        ORDER BY arrival_date DESC
        LIMIT 5;

    """
    cursor.execute(query)  # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        products.append(row)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('book-page-not-logged.html')
    else:
        return render_template('new-arrivals-not-logged.html',
                               products=products)


@app.route('/branches-not-logged')
def go_to_branches_not_logged():
    cursor, connection = db_connector('group31_db')
    cursor.execute('SELECT * FROM branch')
    data = cursor.fetchall()
    branches = []
    for row in data:
        branch = Branch(*row)
        branches.append(branch)
    return render_template('branches-not-logged.html', branches=branches)


@app.route('/log-in')
def login():
    return render_template('log-in.html')


@app.route('/sign-up-librarian', methods=['GET', 'POST'])
def sign_up_librarian():
    if request.method == 'POST':
        data = request.values.to_dict()
        librarian = Librarian(**data)
        librarian.insert_librarian_to_db()
        return render_template('homepage-librarian.html')
    else:
        return render_template('sign-up-librarian.html')


@app.route('/searching-results-not-logged', methods=['GET', 'POST'])
def search_results():
    if request.method == 'POST':
        search_query = request.form.get('search-field')
        results = search_view_func_helper(search_query)
        return render_template('searching-results-not-logged.html', results=results, search_query=search_query)
    if request.method == 'GET':
        search_query = request.args.get('search-field')
        results = search_view_func_helper(search_query)
        return render_template('searching-results-not-logged.html', results=results, search_query=search_query)


@app.route('/book-page-not-logged/<book_name>', methods=['GET', 'POST'])
def book_page(book_name):
    # connect to the database
    cursor, connection = db_connector('group31_db')
    # retrieve the book information from the database
    cursor.execute("SELECT * FROM book WHERE book_name = %s", book_name)
    book = cursor.fetchall()
    # retrieve the branches that have copies of the book
    cursor.execute(
        "SELECT branch.branch_name, branch.branch_phone_num, branch.city, branch.street, branch.house_num, SUM(books_in_branches.stock_in_branch) as stock FROM books_in_branches JOIN branch ON books_in_branches.branch_name = branch.branch_name WHERE book_name = %s GROUP BY branch.branch_name",
        (book_name,))
    branches = cursor.fetchall()
    cursor.close()
    connection.close()
    branch_result = []
    results = []
    for result in branches:
        branch = {
            'branch_name': result[0],
            'branch_phone_num': result[1],
            'city': result[2],
            'street': result[3],
            'house_num': result[4],
            'stock_in_branch': result[5]
        }
        branch_result.append(branch)

    for result in book:
        # create a dictionary with the book information
        book = {
            'author_name': result[1],
            'book_name': result[0],
            'year_of_publish': result[2],
            'description': result[6],
            'publisher': result[3],
            'cover_url': result[5]
        }
        results.append(book)

    return render_template('book-page-not-logged.html', book=book, results=results[0], branch_result=branch_result)


@app.route('/best-sellers-not-logged')
def open_best_sellers_not_logged():
    cursor, connect = db_connector('group31_db')
    cursor.execute('SELECT book.*, COUNT(*) as borrow_count '
                   'FROM borrowing JOIN copy_of_book ON borrowing.book_id = copy_of_book.book_id '
                   'JOIN book ON copy_of_book.book_name = book.book_name '
                   'and copy_of_book.author_name = book.author_name '
                   'GROUP BY book.book_name, book.author_name ORDER BY borrow_count DESC LIMIT 5;')  # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        products.append(row)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('homepage-not-logged.html')
    else:
        return render_template('best-sellers-not-logged.html',
                               products=products)


############################################ logged librarian ##########################################################
@app.route('/homepage-librarian')
def homepage_librarian():
    return render_template('homepage-librarian.html')


@app.route('/insert-book-1', methods=['GET', 'POST'])
def insert_book_in_stock():
    cursor, connection = db_connector('group31_db')
    query = "SELECT branch_name FROM branch"
    cursor.execute(query)
    branches = cursor.fetchall()
    if request.method == 'POST':
        book_name = request.form['book_name']
        branch = request.form['branch']
        author_name = request.form['author_name']
        quantity = int(request.form['quantity'])
        result = check_branch_name(cursor, connection, branch)
        if result is not None:
            return render_template(result)
        # Call your function here to check if the book is in stock
        cursor.execute(
            "SELECT COUNT(*) FROM book WHERE book_name = %s AND author_name = %s",
            (book_name, author_name)
        )
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute(f"select year_of_publish, name_of_publisher from"
                           f" book where book_name = %s and author_name = %s;", (book_name, author_name))
            year_of_publish, publisher = cursor.fetchall()[0]
            cursor.execute(
                "select stock_in_branch from books_in_branches where book_name = %s and author_name = %s "
                "and branch_name = %s",
                (book_name, author_name, branch))
            exist_in_branch = cursor.fetchone()
            if exist_in_branch is not None:
                stock_in_branch = exist_in_branch[0]
                new_copy_of_book = CopyOfBook(book_name, author_name, year_of_publish, publisher, branch)
                new_copy_of_book.insert_multiple_copies(quantity, cursor, connection, stock_in_branch)
                stock_counter = stock_in_branch + quantity
            else:
                new_copy_of_book = CopyOfBook(book_name, author_name, year_of_publish, publisher, branch)
                new_copy_of_book.insert_new_book(quantity)
                connection.commit()
                stock_counter = quantity
            # If the book is in stock, render the insert-book-2-in-stock template
            return render_template('insert-book-2-in-stock.html', book_name=book_name, branch=branch,
                                   quantity=quantity,
                                   stock_counter=stock_counter, author_name=author_name, branches=branches)

        else:
            # If the book is not in stock, render the insert-book-2-not-in-stock template
            return render_template('insert-book-2-not-in-stock.html', book_name=book_name, quantity=quantity,
                                   branch=branch, author_name=author_name)
    return render_template('insert-book-1.html', branches=branches)


#
@app.route('/insert-book-2-not-in-stock', methods=['GET', 'POST'])
def insert_book_not_in_stock():
    cursor, connections = db_connector('group31_db')
    if request.method == 'POST':
        book_name = request.form['book_name']
        branch = request.form['branch']
        author_name = request.form['author_name']
        publish_year = request.form['publish_year']
        quantity = int(request.form['quantity'])
        publish_name = request.form['publish_name']
        new_copy_of_book = CopyOfBook(book_name, author_name, publish_year, publish_name, branch)
        cursor.execute(
            "INSERT INTO book (author_name, book_name, year_of_publish, name_of_publisher, arrival_date,"
            " cover_photo, book_description)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (author_name, book_name, publish_year, publish_name,
             new_copy_of_book.arrival_date, new_copy_of_book.cover_photo, new_copy_of_book.description)
        )
        connections.commit()
        new_copy_of_book.insert_new_book(quantity)
        stock_counter = quantity

        # If the book is in stock, render the insert-book-2-in-stock template
        return render_template('insert-book-2-in-stock.html', book_name=book_name, branch=branch, quantity=quantity,
                               stock_counter=stock_counter, author_name=author_name, publish_name=publish_name,
                               publish_year=publish_year)


@app.route('/new-arrivals-librarian', methods=['GET', 'POST'])
def go_to_new_arrivals_librarian():
    cursor, connect = db_connector('group31_db')
    query = """
            SELECT *
            FROM book
            WHERE cover_photo IS NOT NULL AND book_description IS NOT NULL
            ORDER BY arrival_date DESC
            LIMIT 5;

        """
    cursor.execute(query)  # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        products.append(row)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('book.html')
    else:
        return render_template('new-arrivals-librarian.html', products=products)


@app.route('/branches-librarian', methods=['GET', 'POST'])
def go_to_branches_librarian():
    cursor, connection = db_connector('group31_db')
    cursor.execute('SELECT * FROM branch')
    data = cursor.fetchall()
    branches = []
    for row in data:
        branch = Branch(*row)
        branches.append(branch)
    return render_template('branches-librarian.html', branches=branches)


@app.route('/borrow-book-librarian-1', methods=['GET', 'POST'])
def borrow_book():
    cursor, connect = db_connector('group31_db')
    if request.method == 'POST':
        if 'email' in session:
            email = request.form['email']
            data = request.values.to_dict()
            branch_name = session['branch']
            data['branch_name'] = branch_name
            if book_exists(data['book_name'], data['author']):
                if check_librarian_and_book_same_branch(cursor, connect,
                                                        branch_name, data['book_name'], data['author']):
                    if check_less_then_three_books_borrowed(cursor, connect, email):
                        new_borrow = BorrowBook(**data)
                        book_id = new_borrow.borrow_book()
                        if not book_id:
                            return render_template('borrow-book-2-not-available.html')
                        else:
                            book_name = request.form['book_name']
                            author_name = request.form['author']
                            borrows = Borrows(email, book_id)
                            stock_counter = borrows.borrowing_doc(book_name, author_name, branch_name)

                            return render_template('borrow-book-librarian-2-successful.html', book_name=book_name,
                                                   author_name=author_name,
                                                   branch=branch_name, stock_counter=stock_counter)
                    else:
                        return render_template('borrow-3-books.html')
                else:
                    return render_template('borrow-book-2-not-available.html')
            else:
                return render_template('borrow-book-2-not-available.html')
    else:
        return render_template('borrow-book-librarian-1.html')


@app.route('/borrow-3-books')
def borrowed_3_books():
    return render_template('borrow-3-books.html')


@app.route('/borrow-book-2-not-available')
def borrow_book_not_available():
    return render_template('borrow-book-2-not-available.html')


@app.route('/return-book-librarian-1', methods=['GET', 'POST'])
def return_book_librarian():
    cursor, connection = db_connector('group31_db')
    if request.method == 'POST':
        data = request.values.to_dict()
        branch = session['branch']
        data['branch_name'] = branch
        book_name = data['book_name']
        author_name = data['author']
        borrow = BorrowBook(**data)
        book_id = borrow.returning_book()
        if book_id:
            cursor.execute("SELECT stock_in_branch FROM books_in_branches "
                           "WHERE book_name = %s "
                           "AND author_name = %s"
                           "AND branch_name = %s", (book_name, author_name, branch))
            stock_counter = cursor.fetchone()
            if stock_counter is not None:
                stock_counter = stock_counter[0]
            else:
                stock_counter = 0
            return render_template('return-book-librarian-2.html',
                                   branch=branch,
                                   book_name=book_name,
                                   author_name=author_name,
                                   stock_counter=stock_counter
                                   )
        else:
            return render_template('return-book-error.html')
    else:
        return render_template('return-book-librarian-1.html')


@app.route('/return-book-error')
def return_book_error():
    return render_template('return-book-error.html')


@app.route('/book-page-librarian/<book_name>', methods=['GET', 'POST'])
def book_page_librarian(book_name):
    # connect to the database
    cursor, connection = db_connector('group31_db')
    # retrieve the book information from the database
    cursor.execute("SELECT * FROM book WHERE book_name = %s", (book_name,))
    book = cursor.fetchall()
    # retrieve the branches that have copies of the book
    cursor.execute(
        "SELECT branch.branch_name, branch.branch_phone_num,"
        " branch.city, branch.street, branch.house_num,"
        " SUM(books_in_branches.stock_in_branch) as stock FROM books_in_branches "
        "JOIN branch ON books_in_branches.branch_name = branch.branch_name "
        "WHERE book_name = %s GROUP BY branch.branch_name",
        (book_name,))
    branches = cursor.fetchall()
    cursor.close()
    connection.close()
    branch_result = []
    results = []
    for result in branches:
        branch = {
            'branch_name': result[0],
            'branch_phone_num': result[1],
            'city': result[2],
            'street': result[3],
            'house_num': result[4],
            'stock_in_branch': result[5]
        }
        branch_result.append(branch)

    for result in book:
        # create a dictionary with the book information
        book = {
            'author_name': result[1],
            'book_name': result[0],
            'year_of_publish': result[2],
            'description': result[6],
            'publisher': result[3],
            'cover_url': result[5]
        }
        results.append(book)

    return render_template('book-page-librarian.html', book=book, results=results[0], branch_result=branch_result)


@app.route('/sign-up-subscriber-librarian', methods=['GET', 'POST'])
def sign_up_subscriber_librarian():
    if request.method == 'POST':
        data = request.values.to_dict()
        subscriber = Subscriber(**data)
        subscriber.insert_to_db()
        return render_template('homepage-librarian.html')
    else:
        return render_template('sign-up-subscriber-librarian.html')


@app.route('/searching-results-librarian', methods=['GET', 'POST'])
def search_results_librarian():
    if request.method == 'POST':
        search_query = request.form.get('search-field')
        results = search_view_func_helper(search_query)
        return render_template('searching-results-librarian.html', results=results, search_query=search_query)
    if request.method == 'GET':
        search_query = request.args.get('search-field')
        results = search_view_func_helper(search_query)
        return render_template('searching-results-librarian.html', results=results, search_query=search_query)


@app.route('/best-sellers-librarian')
def open_best_sellers_librarian():
    cursor, connect = db_connector('group31_db')
    cursor.execute('SELECT book.*, COUNT(*) as borrow_count '
                   'FROM borrowing JOIN copy_of_book ON borrowing.book_id = copy_of_book.book_id '
                   'JOIN book ON copy_of_book.book_name = book.book_name '
                   'and copy_of_book.author_name = book.author_name '
                   'GROUP BY book.book_name, book.author_name ORDER BY borrow_count DESC LIMIT 5;')  # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        products.append(row)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('homepage-librarian.html')
    else:
        return render_template('best-sellers-librarian.html',
                               products=products)


############################################ logged subscriber #########################################################
@app.route('/sign-up-subscriber', methods=['GET', 'POST'])
def sign_up_subscriber():
    if request.method == 'POST':
        data = request.values.to_dict()
        subscriber = Subscriber(**data)
        subscriber.insert_to_db()
        return render_template('homepage-subscriber.html')
    else:
        return render_template('sign-up-subscriber.html')


@app.route('/homepage-subscriber')
def homepage_subscriber():
    return render_template('homepage-subscriber.html')


@app.route('/new-arrivals-subscriber')
def new_arrivals_subscriber():
    cursor, connect = db_connector('group31_db')
    query = """
            SELECT *
            FROM book
            WHERE cover_photo IS NOT NULL AND book_description IS NOT NULL
            ORDER BY arrival_date DESC
            LIMIT 5;

        """
    cursor.execute(query)  # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        products.append(row)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('homepage-subscriber.html')
    else:
        return render_template('new-arrivals-subscriber.html',
                               products=products)


@app.route('/branches-subscriber')
def go_to_branches_subscriber():
    cursor, connection = db_connector('group31_db')
    cursor.execute('SELECT * FROM branch')
    data = cursor.fetchall()
    branches = []
    for row in data:
        branch = Branch(row[0], row[1], row[2], row[3], row[4])
        branches.append(branch)
    return render_template('branches-subscriber.html', branches=branches)


@app.route('/homepage-not-logged')
def log_out():
    # Get the user's email address from the request
    if 'email' in session:
        email = session['email']
        # Remove the user's email address from the session data
        session.pop(email, None)
    # Redirect the user to the sign in page
    return redirect('/')


@app.route('/borrows-subscriber')
def borrowing_history():
    cursor, connection = db_connector('group31_db')
    if 'email' in session:
        email = session['email']
        data = borrowing_history_helper(cursor, connection, email)
        subscriber = Subscriber(**data)
        borrowing = subscriber.borrowing_history()
        order = subscriber.order_history()
        return render_template('borrows-subscriber.html', borrowing=borrowing, order=order)


@app.route('/book-page-subscriber/<book_name>', methods=['GET', 'POST'])
def book_page_subscriber(book_name):
    # connect to the database
    cursor, connection = db_connector('group31_db')
    # retrieve the book information from the database
    cursor.execute("SELECT * FROM book WHERE book_name = %s", (book_name,))
    book = cursor.fetchall()
    # retrieve the branches that have copies of the book
    cursor.execute(
        "SELECT branch.branch_name, branch.branch_phone_num, branch.city,"
        " branch.street, branch.house_num, "
        "SUM(books_in_branches.stock_in_branch) as stock FROM books_in_branches "
        "JOIN branch ON books_in_branches.branch_name = branch.branch_name "
        "WHERE book_name = %s GROUP BY branch.branch_name",
        (book_name,))
    branches = cursor.fetchall()
    cursor.close()
    connection.close()
    branch_result = []
    results = []
    for result in branches:
        branch = {
            'branch_name': result[0],
            'branch_phone_num': result[1],
            'city': result[2],
            'street': result[3],
            'house_num': result[4],
            'stock_in_branch': result[5]
        }
        branch_result.append(branch)

    for result in book:
        # create a dictionary with the book information
        book = {
            'author_name': result[1],
            'book_name': result[0],
            'year_of_publish': result[2],
            'description': result[6],
            'publisher': result[3],
            'cover_url': result[5]
        }
        results.append(book)

    return render_template('book-page-subscriber.html', book=book, results=results[0], branch_result=branch_result)


@app.route('/extension', methods=['GET', 'POST'])
def extension():
    cursor, connection = db_connector('group31_db')
    if 'email' in session:
        email = session['email']
        borrowing = extension_helper(cursor, connection, email)
        if request.method == 'POST':
            if request.form.get('extension'):
                book_id = request.form.get('book_id')
                borrow = Borrows(email, book_id)
                new_date = datetime.strptime(request.form.get('date_of_borrowing'), "%Y-%m-%d") + timedelta(days=21)
                extension_ans = borrow.extension(new_date)
                if extension_ans == 'extension_approved':
                    return extension_approved(new_date)
                elif extension_ans == 'extension_rejected':
                    return extension_rejected()
        return render_template('extension.html', borrowing=borrowing)


@app.route('/extension-approved')
def extension_approved(new_date):
    return render_template('extension-approved.html', new_date=new_date)


@app.route('/extension-rejected')
def extension_rejected():
    return render_template('extension-rejected.html')


from mysql.connector import Error


@app.route('/order-book', methods=['POST', 'GET'])
def order_book():
    email = session['email']
    cursor, connect = db_connector('group31_db')
    query = "SELECT branch_name FROM branch"
    cursor.execute(query)
    branches = cursor.fetchall()
    cursor.close()
    connect.close()
    if request.method == 'POST':
        try:
            new_order = OrderBook(email)
            redirect_to = new_order.order_book()
            return render_template(redirect_to)
        except Error as e:
            print(e)
    return render_template('order-book.html', branches=branches)


@app.route('/order-book-rejected-not-in-stock')
def order_book_not_in_stock():
    return render_template('order-book-rejected-not-in-stock.html')


@app.route('/order-book-rejected-ordered')
def order_book_pre_ordered():
    return render_template('order-book-rejected-ordered.html')


@app.route('/order-book-approved')
def order_book_approved():
    return render_template('order-book-approved.html')


@app.route('/order-book-error')
def order_book_error():
    return render_template('order-book-error.html')


@app.route('/searching-results-subscriber', methods=['GET', 'POST'])
def search_results_subscriber():
    if request.method == 'POST':
        search_query = request.form.get('search-field')
        results = search_view_func_helper(search_query)
        return render_template('searching-results-subscriber.html', results=results, search_query=search_query)
    if request.method == 'GET':
        search_query = request.args.get('search-field')
        results = search_view_func_helper(search_query)
        return render_template('searching-results-subscriber.html', results=results, search_query=search_query)


@app.route('/best-sellers-subscriber')
def open_best_sellers_subscriber():
    cursor, connect = db_connector('group31_db')
    cursor.execute('SELECT book.*, COUNT(*) as borrow_count '
                   'FROM borrowing JOIN copy_of_book ON borrowing.book_id = copy_of_book.book_id '
                   'JOIN book ON copy_of_book.book_name = book.book_name '
                   'and copy_of_book.author_name = book.author_name '
                   'GROUP BY book.book_name, book.author_name ORDER BY borrow_count DESC LIMIT 5;')  # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        products.append(row)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('homepage-subscriber.html')
    else:
        return render_template('best-sellers-subscriber.html',
                               products=products)


##################################### daily check for returning books ##################################################
def connect_and_get_date():
    cursor, connection = db_connector('group31_db')
    today = datetime.today().date()
    return cursor, connection, today


def get_overdue_books(cursor, today):
    cursor.execute("SELECT book_id, email FROM borrowing WHERE date_of_return = %s", (today,))
    return cursor.fetchall()


def update_copy_of_book_table(cursor, book_id):
    cursor.execute("SELECT COUNT(*) FROM book_order "
                   "WHERE book_id = %s "
                   "AND order_status = 'pending'", book_id)
    num_of_rows = cursor.fetchone()

    # If the book is ordered, update the order status and estimated arrival date
    if num_of_rows[0] > 0:
        cursor.execute("SELECT email FROM book_order WHERE book_id = %s", book_id)
        email = cursor.fetchone()[0]
        cursor.execute(f"UPDATE copy_of_book SET copy_of_book_status = 'ordered by {email}'"
                       f"WHERE book_ID = %s",
                       book_id)

    else:
        cursor.execute("UPDATE copy_of_book SET copy_of_book_status = 'available' WHERE book_ID = %s", (book_id,))
    query = 'UPDATE books_in_branches SET stock_in_branch = stock_in_branch + 1 ' \
            'WHERE book_name = (SELECT book_name FROM copy_of_book WHERE book_id = %s) AND ' \
            'author_name = (SELECT author_name FROM copy_of_book WHERE book_id = %s) AND' \
            ' branch_name = (SELECT branch_name FROM copy_of_book WHERE book_id = %s)'
    cursor.execute(query, (book_id, book_id, book_id))


def update_subscriber_table(cursor, email):
    cursor.execute("UPDATE subscriber SET quantity_of_borrowed_books = quantity_of_borrowed_books - 1 WHERE email = %s",
                   (email,))


def return_overdue_books():
    cursor, connection, today = connect_and_get_date()

    # Check for overdue books in the "borrowing" table
    cursor.execute("SELECT book_id, email FROM borrowing WHERE date_of_return + INTERVAL 14 DAY = %s", (today,))
    overdue_books = cursor.fetchall()
    for book_id, email in overdue_books:
        update_copy_of_book_table(cursor, book_id)
        update_subscriber_table(cursor, email)

    # Check for overdue books in the "book_order" table
    cursor.execute("SELECT book_id, email FROM book_order WHERE order_status='ordered' "
                   "AND date_of_order + INTERVAL 3 DAY = %s", (today,))
    overdue_books = cursor.fetchall()
    for book_id, email in overdue_books:
        update_copy_of_book_table(cursor, book_id)
        cursor.execute("UPDATE book_order SET order_status='not borrowed' WHERE book_id = %s", (book_id,))
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    app.run(debug=True)
    while True:
        return_overdue_books()
        time.sleep(86400)  # sleep for 86400 seconds, or 24 hours