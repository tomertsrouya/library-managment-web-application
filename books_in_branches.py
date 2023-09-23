from Order_book import OrderBook
from db_connection import db_connector
class BooksInBranches():
    def __init__(self, stock_in_branch, branch_name, author_name, book_name):
        self.stock_in_branch = stock_in_branch
        self.branch_name = branch_name
        self.author_name = author_name
        self.book_name = book_name




    def num_of_copies(self):
        cursor, connect = db_connector('group31_db')
        cursor.execute(f"select stock_in_branch from books_in_branches where book_name = '{self.book_name}"
                       f"and branch_name = '{self.branch_name}'")
        num_of_copies = cursor.fetchall() # or one
        cursor.close()
        connect.close()
        return num_of_copies

    def order_book(self):
        if self.stock_in_branch == 0:
            cursor, connection = db_connector('group31_db')
            query = "select order_status "





    def order_to_borrow(self): #complete
        pass



