"""
call.py - Telemarketing script that displays the next name 
          and phone number of a Customer to call.

          This script is used to drive promotions for 
          specific customers based on their order history.
          We only want to call customers that have placed
          an order of over 20 Watermelons.

"""

import sqlite3
import datetime

DB = None
CONN = None

# Class definition to store our customer data
class Customer(object):
	def __init__(self, id_num, first, last, telephone, last_called):
		self.id = id_num
		self.first = first
		self.last = last
		self.telephone = telephone
		self.last_called = last_called

	def __str__(self):
		output = "Name: %s, %s\n" % (self.last, self.first)
		output += "Phone: %s" % self.telephone

		return output

# Connect to the Database
def connect_to_db():
	global DB, CONN
	CONN = sqlite3.connect('melons.db')

	DB = CONN.cursor()


# Retrieve the next uncontacted customer record from the database.
# Return the data in a Customer class object.
#
# Remember: Our telemarketers should only be calling customers
#           who have placed orders of 20 melons or more.
def generate_list():

	query1 = """CREATE VIEW OrdersOver20View AS 
				SELECT * 
			   	FROM 
			   		(SELECT order_id, SUM(quantity) AS total_quantity 
			   		FROM order_items 
			   		GROUP BY order_id) 
			   	WHERE total_quantity > 20;"""
	DB.execute(query1)

	query2 = """CREATE VIEW CustomerIDsOver20View AS 
				SELECT ov.order_id, ov.total_quantity,o.customer_id 
				FROM OrdersOver20View AS ov 
				INNER JOIN orders AS o ON (ov.order_id=o.id);"""
	DB.execute(query2)

	query3 = """SELECT c.id, c.givenname, c.surname, c.telephone, c.last_called, COUNT(o.order_id) AS Orders_over_20 
				FROM customers AS c 
				INNER JOIN CustomerIDsOver20View AS o ON (c.id=o.customer_id) 
				GROUP BY c.id;"""
	DB.execute(query3)
	customer_rows = DB.fetchall()

	query4 = """DROP VIEW OrdersOver20View""";
	DB.execute(query4)

	query5 = """DROP VIEW CustomerIDsOver20View""";
	DB.execute(query5)

	return customer_rows

def get_next_customer(customer_rows):

	for customer in customer_rows:
		c = Customer(customer[0], customer[1], customer[2], customer[3], customer[4])
		if c.last_called == None:
			return c

def display_next_to_call(customer):
	print "---------------------"
	print "Next Customer to call"
	print "---------------------\n"
	print customer
	print "\n"


# Update the "last called" column for the customer
#   in the database.
def update_customer_called(customer):

	query = """UPDATE customers
			   SET last_called = ?
			   WHERE id = ?;"""
	date = datetime.date.today()
	customer_id = customer.id

	DB.execute(query,(date,customer_id))
	CONN.commit()

	query2 = """SELECT *
				FROM customers
				WHERE id = ?;"""

	DB.execute(query2,(customer_id,))
	customer = DB.fetchall()

	print customer

def main():
	connect_to_db()

	customer_rows = generate_list()

	done = False

	while not done:
		customer = get_next_customer(customer_rows)
		display_next_to_call(customer)

		print "Mark this customer as called?"
		user_answer = raw_input('(y/n) > ')

		if user_answer.lower() == 'y':
			update_customer_called(customer)
		else:
			done = True

if __name__ == '__main__':
	main()