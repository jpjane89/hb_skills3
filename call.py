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

	def display(self):
		print "---------------------"
		print "Next Customer to call"
		print "---------------------\n"
		print self
		print "\n"

	def update_customer_called(self):

		query = """UPDATE customers
				   SET last_called = ?
				   WHERE id = ?;"""
		date = datetime.date.today()

		DB.execute(query,(date,self.id))
		CONN.commit()


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
	query = """
			SELECT DISTINCT c.id, c.givenname, c.surname, c.telephone, c.last_called
			FROM customers AS c
			INNER JOIN orders AS o ON (o.customer_id = c.id)
			INNER JOIN order_items AS o_i ON (o_i.order_id = o.id)
			GROUP BY o.id
			HAVING SUM(o_i.quantity) >= 20
			ORDER BY c.id ASC;
			"""
	DB.execute(query)
	customer_rows = DB.fetchall()

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
def main():
	connect_to_db()

	customer_rows = generate_list()

	done = False

	while not done:
		customer = get_next_customer(customer_rows)
		customer.display()

		print "Mark this customer as called?"
		user_answer = raw_input('(y/n) > ')

		if user_answer.lower() == 'y':
			customer.update_called()
		else:
			done = True

if __name__ == '__main__':
	main()