"""
This is class Branch, here we have all the action to do with the branch
"""
from Book import Book
from db_connection import db_connector
class Branch():
    def __init__(self, branch_name, branch_phone_num, city, street, house_num):
        self.branch_name = branch_name
        self.branch_phone_num = branch_phone_num
        self.city = city
        self.street = street
        self.house_num = house_num





