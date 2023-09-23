from db_connection import db_connector

# delete branches
def query_is_book_name(query):
    cursor, conn = db_connector('group31_db')
    cursor.execute(f"SELECT * FROM books WHERE book_name = %s", (query,))
    book = cursor.fetchone()
    # Close the database connection
    cursor.close()
    conn.close()
    # Return True if a book was found, False otherwise
    return book is not None


def query_is_author_name(query):
    cursor, conn = db_connector('group31_db')
    cursor.execute(f"SELECT * FROM book WHERE author_name = %s", (query,))
    author = cursor.fetchone()
    # Close the database connection
    cursor.close()
    conn.close()
    # Return True if a book was found, False otherwise
    return author is not None

def query_is_branch_name(query):
    cursor, conn = db_connector('group31_db')
    cursor.execute(f"SELECT * FROM branch WHERE branch_name = %s", (query,))
    branch = cursor.fetchone()
    # Close the database connection
    cursor.close()
    conn.close()
    # Return True if a book was found, False otherwise
    return branch is not None


def search_database(query):
    # Connect to the database
    cursor, conn = db_connector('group31_db')
    # Check if the query is a book name, author name, or branch name
    if query_is_book_name(query):
        # Search for books by book name
        cursor.execute("SELECT * FROM books WHERE book_name LIKE %s", ('%' + query + '%',))
        results = cursor.fetchall()
    elif query_is_author_name(query):
        # Search for books by author name
        cursor.execute("SELECT * FROM books WHERE author LIKE %s", ('%' + query + '%',))
        results = cursor.fetchall()
    elif query_is_branch_name(query):
        # Search for books in a branch
        cursor.execute("SELECT * FROM books_in_branches WHERE branch_name = %s", (query,))
        results = cursor.fetchall()
        # Also retrieve the branch information
        cursor.execute("SELECT * FROM branch WHERE branch_name = %s", (query,))
        branch = cursor.fetchone()
    else:
        # Return an empty result set if the query is not recognized
        results = []
        branch = None

    # Close the database connection
    cursor.close()
    conn.close()

    return results, branch


def search_view_func_helper(search_query):
# search the database for books with a matching title or author name
        cursor, connection = db_connector('group31_db')
        cursor.execute("SELECT * FROM book WHERE book_name LIKE %s OR author_name LIKE %s",
                       ('%' + search_query + '%', '%' + search_query + '%'))
        search_results = cursor.fetchall()
        cursor.close()
        connection.close()
        # create a list of dictionaries with the search results
        results = []
        for result in search_results:
            # create a dictionary with the book information
            book = {
                'author_name': result[1],
                'book_name': result[0],
                'year_of_publish': result[2],
                'description': result[6],
                'publisher': result[3],
                'cover_url': result[5]
            }
            # add the book to the list of results
            results.append(book)
        # render the search results template
        return results

