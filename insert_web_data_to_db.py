# logout --> num 10
# navbar --> num 11
# num 12
### html, css ###
import pymysql

from Subscriber import Subscriber
from db_connection import db_connector
from get_book_info import get_book_information, get_book_cover
from Book import Book
from search import search_database
from Librarian import Librarian
from datetime import datetime
from books_in_branches import BooksInBranches
"""
This is the main page of the project, here we will gather all of our functions and classes.
"""

from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def redirect_sign_up():
    if request.method == 'POST':
        book_name = request.form['book_name']
        branch = request.form['branch']
        author_name = request.form['author_name']
        quantity = request.form['quantity']
        stock_counter = 1 #function that counts the quantity of a certain book by its {{book_name}} and {{author_name}} in the {{branch}}

        # Call your function here to check if the book is in stock
        #book_in_stock = check_if_book_in_stock(book_name, branch)

        if book_name == 'noga':
            if author_name == 'noga':
                stock_counter += int(quantity)
                # If the book is in stock, render the insert-book-2-in-stock template
                return render_template('insert-book-2-in-stock.html', book_name=book_name, branch=branch, quantity=quantity, stock_counter=stock_counter, author_name=author_name)
        else:
            # If the book is not in stock, render the insert-book-2-not-in-stock template
            return render_template('insert-book-2-not-in-stock.html', book_name=book_name, quantity=quantity, branch=branch, author_name=author_name)
    return render_template('insert-book-1.html')


# @app.route('/')
# def tryy(): # understand how to use book title
#     book_description, publisher, publish_date, author = get_book_information('The Alchemist')
#     book_cover_image_url = get_book_cover('The Alchemist')
#     return render_template('book.html', book_title='The Alchemist', book_description=book_description,
#                            publisher=publisher, publish_date=publish_date, author_name=','.join(author),
#                            book_cover_image_url=book_cover_image_url)




# @app.route('/', methods=['POST', 'GET'])
# def insert_book():
#     try:
#         if request.method == 'POST':
#             book_name = request.form['book_name']
#             branch = request.form['branch-name']
#             book_description, publisher, year_of_publish, author = get_book_information(book_name)
#             new_book_to_insert = Book(book_name, author, year_of_publish, publisher, branch=branch)
#             new_book_to_insert.insert_new_book()
#             if new_book_to_insert == f'The book {book_name} is already in the data base':
#                 new_book_to_insert.find_in_stock()
#             return render_template('homepage-librarian.html')
#     except pymysql.err.DataError as e:
#         print(e.args)
#     else:
#         return render_template('insert-book-1.html')
#
#
# @app.route('/')
# def home():
#     return render_template('homepage-not-logged.html')



# @app.route('/Sign up', methods=['GET', 'POST'])
# def view_func():
#
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#
#         # # Validate login credentials
#         # if valid_login(email, password):
#         #     # Login successful, redirect to homepage
#         #     return redirect(url_for('home'))
#         # else:
#         #     # Login failed, display error message
#         #     error = 'Invalid email or password'
#
#         return render_template('homepage-not-logged.html', email=email, password=password)
#     else:
#         # Render the login HTML page
#         return render_template('Sign up.html')






# @app.route('/sign up as subscriber', methods=['GET', 'POST'])
def sign_up_subscriber_to_home():
    if request.method == 'POST':
        cursor, connect = db_connector('library')
        email = request.form['email']
        full_name = request.form['name']
        birth_date = request.form['birth_date']
        phone_num = request.form['phone']
        password = request.form['password']
        address = request.form['address']

        cursor.execute('INSERT INTO subscriber(email, password, phone_num, address, full_name) '
                       'VALUES(%s, %s, %s, %s, %s)',
                       (email, password, phone_num, address, full_name))
        connect.commit()
        cursor.close()
        connect.close()
        new_subscriber = Subscriber(email, full_name, birth_date, phone_num, address)
        new_subscriber.insert_to_db()
        return render_template('/homepage-not-logged.html')
    else:
        return render_template('/sign up as subscriber.html')





@app.route('/sign up as worker', methods=['GET', 'POST']) # add password to db
def sign_up_librarian_to_home():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        phone_num = request.form['phone']
        city = request.form['city']
        street = request.form['street']
        apartment = request.form['apartment']
        beginning_date = datetime.strptime(request.form['beginningdate'], '%Y-%m-%d')
        branch = request.form['branch']
        # password = request.form['password']
        new_librarian = Librarian(email=email,
                                  first_name=first_name,
                                  last_name=last_name,
                                  phone_num=phone_num,
                                  city=city,
                                  street=street,
                                  apartment=apartment,
                                  beginning_date=beginning_date,
                                  branch=branch)
        new_librarian.insert_librarian_to_db()
        return render_template('homepage-not-logged.html') # return to hoe logged in as librarian
    else:
        return render_template('sign up as worker.html')


@app.route('/book', methods=['GET', 'POST'])
def get_to_book():
    if request.method == 'POST':
        cursor, connect = db_connector('library')
        # check if the book is available
        render_template('home.html')
    else:
        render_template('book.html')


@app.route('/new-arrivals-subscriber', methods=['GET', 'POST']) # take the X first books from db
def home_to_new_arrivals_subscriber():
    cursor, connect = db_connector('library')
    cursor.execute('select * from book limit 5') # add to data base in lifo
    data = cursor.fetchall()
    products = []
    for row in data:
        new_book = Book(row[0], row[1], row[2], row[3], row[4], datetime.today())
        products.append(new_book)
    cursor.close()
    connect.close()
    if request.method == 'POST':
        return render_template('home.html')
    else:
        return render_template('new-arrivals-subscriber.html',
                               products=products)


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = search_database(query)
    return render_template('search_results.html', results=results)


#
# @app.route('/', methods=['GET', 'POST'])
# def redirect_sign_up():
#     if request.method == 'POST':
#         book_name = request.form['book_name']
#         branch = request.form['branch']
#         author_name = request.form['author_name']
#         quantity = request.form['quantity']
#         stock_counter = 1 #function that counts the quantity of a certain book by its {{book_name}} and {{author_name}} in the {{branch}}
#
#         # Call your function here to check if the book is in stock
#         #book_in_stock = check_if_book_in_stock(book_name, branch)
#
#         if book_name == 'noga':
#             if author_name == 'noga':
#                 stock_counter += int(quantity)
#                 # If the book is in stock, render the insert-book-2-in-stock template
#                 return render_template('insert-book-2-in-stock.html', book_name=book_name, branch=branch, quantity=quantity, stock_counter=stock_counter, author_name=author_name)
#         else:
#             # If the book is not in stock, render the insert-book-2-not-in-stock template
#             return render_template('insert-book-2-not-in-stock.html', book_name=book_name, quantity=quantity, branch=branch, author_name=author_name)
#     return render_template('insert-book-1.html')
#



@app.route('/insert-book-2-not-in-stock', methods=['GET', 'POST'])
def insert_book_not_in_stock():
    if request.method == 'POST':
        book_name = request.form['book_name']
        branch = request.form['branch']
        author_name = request.form['author_name']
        publish_year = request.form['publish_year']
        quantity = request.form['quantity']
        publish_name = request.form['publish_name']
        stock_counter = 1 #function that counts the quantity of a certain book by its {{book_name}} and {{author_name}} in the {{branch}}
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be a positive integer")
        except ValueError:
            return "Please enter a valid quantity"

        if book_name and branch and author_name and publish_year and publish_name and quantity:
            stock_counter += int(quantity)
            # If the book is in stock, render the insert-book-2-in-stock template
            return render_template('insert-book-2-in-stock.html', book_name=book_name, branch=branch, quantity=quantity, stock_counter=stock_counter, author_name=author_name, publish_name=publish_name, publish_year=publish_year)
        else:
            raise ValueError("Fill All Fields")









if __name__ == '__main__':
    app.run(debug=True)


