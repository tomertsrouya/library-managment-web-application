"""
Class representing a Book object, which has several attributes such as book_name, author, year_of_publish, publisher,
 arrival_date, description, and cover_photo. The class also has an __init__ method that initializes the attributes of
  the object, and also performs several actions related to connecting to a MySQL database and fetching data related to
   the book.
"""
from datetime import datetime
from get_book_info import get_book_cover, get_book_information
from db_connection import db_connector


class Book:
    def __init__(self, book_name, author, year_of_publish, publisher, arrival_date=datetime.today()):
        # Initialize a connection to the database
        cursor, connection = db_connector('group31_db')

        # Set the book name, author, year of publish, publisher, and arrival date as attributes of the class
        self.book_name = book_name
        self.author = author
        self.year_of_publish = year_of_publish
        self.publisher = publisher
        self.arrival_date = arrival_date

        # Retrieve the book description from the database
        cursor.execute(
            "SELECT book_description FROM book WHERE book_name = %s AND author_name = %s",
            (self.book_name, self.author)
        )

        # Fetch the retrieved description
        row = cursor.fetchone()

        # If the book is already in the database, set the description as an attribute of the class
        if row is not None:
            description = row[0]
            self.description = description

        # If the book is not in the database, retrieve the description from another source and set it as an attribute of the class
        else:
            self.description = get_book_information(self.book_name, self.author)
            if self.description is None:
                self.description = "Sorry, we could not get the description, but you can come to dexster's library " \
                                   "and check it out!"
            else:
                self.description = self.description[0]
                if self.description is None:
                    self.description = "Sorry, we could not get the description, but you can come to dexster's library " \
                                       "and check it out!"
                else:
                    self.description = self.description

        # Retrieve the book cover from the database
        cursor.execute(
            "SELECT cover_photo FROM book WHERE book_name = %s AND author_name = %s",
            (self.book_name, self.author)
        )

        # Fetch the retrieved cover
        row = cursor.fetchone()

        # If the book is already in the database, set the cover as an attribute of the class
        if row is not None:
            cover_photo = row[0]
            self.cover_photo = cover_photo

        # If the book is not in the database, retrieve the cover from another source and set it as an attribute of the class
        else:
            self.cover_photo = get_book_cover(self.book_name)
            if self.cover_photo is None:
                self.cover_photo = '/static/assets/Untitled-Artwork.png'
            else:
                self.cover_photo = self.cover_photo






