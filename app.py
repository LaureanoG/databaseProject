from flask import Flask, render_template, request, redirect, url_for, session
from random import seed, randint
import time
import sqlite3

app = Flask(__name__)


# Login info for default admin
# Username: Admin
# Password: Password

# Login info for default customer
# Username: Customer
# Password: Password

@app.route('/', methods=['GET', 'POST'])
def initialize():
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    file = open('CreateTable.txt', 'r')
    for i in file.readlines():
        cursor.execute(i)
    connector.commit()
    return render_template("login.html", msg='Welcome to LLN Resto!')


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and request.form['username'] != "" and request.form['password'] != "":
        username = request.form['username']
        password = request.form['password']
        connector = sqlite3.connect('database.db')
        cursor = connector.cursor()
        if 'Admin' == request.form['login']:
            cursor.execute('SELECT Password FROM Administrator WHERE Username = (?);', (username,))
        if 'Customer' == request.form['login']:
            cursor.execute('SELECT Password FROM Customer WHERE Username = (?);', (username,))
        try:
            passwordDb = cursor.fetchone()[0]
        except TypeError:
            return render_template("login.html", msg="Please fill out the form completely")

        if password == str(passwordDb):
            msg = username + 'has logged in successfully'
            if 'Admin' == request.form['login']:
                return render_template("homeAdmin.html")
            if 'Customer' == request.form['login']:
                return render_template("homeCustomer.html")
        else:
            msg = 'The provided credentials do not match our records.\nPlease try again.'
    elif request.method == "POST":
        msg = 'Please fill out the form completely'
    else:
        msg = 'Welcome to LLN Resto!'
    return render_template("login.html", msg=msg)


@app.route('/homeAdmin', methods=['GET', 'POST'])
def homeAdmin():
    return render_template('homeAdmin.html')


@app.route('/homeCustomer', methods=['GET', 'POST'])
def homeCustomer():
    return render_template('homeCustomer.html')


@app.route("/cart", methods=['GET', 'POST'])
def cart():
    #When cart generates an orderid make sure to send it to orderhistory too
    return render_template("cart.html")


@app.route("/menuCustomer", methods=['GET', 'POST'])
def menuCustomer():
    return render_template("menuCustomer.html")


@app.route("/menuAdmin", methods=['GET', 'POST'])
def menuAdmin():
    return render_template("menuAdmin.html")


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return render_template("admin.html")


@app.route('/manageCustomers', methods=['GET', 'POST'])
def manageCustomers():
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    cursor.execute('SELECT * FROM Customer;')
    #if request.method == "POST" and
    return render_template('manageCustomers.html', data=cursor)


@app.route('/delete/<int:CustomerID>', methods=['GET', 'POST'])
def deleteCustomer(CustomerID):
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    cursor.execute("DELETE FROM Customer WHERE CustomerID = (?)", (CustomerID, ))
    connector.commit()
    cursor.execute('SELECT * FROM Customer;')
    return render_template('manageCustomers.html', data=cursor)


@app.route('/addCustomerForm', methods=['GET', 'POST'])
def addCustomerForm():
    msg = ''
    # Form is filled
    if request.method == "POST" and request.form['Fname'] and request.form['Lname'] and request.form['Address'] and \
            request.form['City'] and request.form['Username'] and request.form['Password'] and request.form['State'] \
            and request.form['ZipCode'] and request.form['PhoneNumber'] and request.form['Email']:
        # Add to customer table with the info requested
        seed(time.time())
        connector = sqlite3.connect('database.db')
        cursor = connector.cursor()
        cursor.execute('INSERT INTO Customer Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', \
        (randint(0, 100000), request.form['Fname'], request.form['Lname'], request.form['Username'], request.form['Password'], \
         request.form['Address'], request.form['City'], request.form['State'], request.form['ZipCode'], \
         request.form['Email'], request.form['PhoneNumber']))
        connector.commit()
        cursor.execute('SELECT * FROM Customer;')
        return render_template('manageCustomers.html', data = cursor)
    elif request.method == "POST":  # Form is not filled
        msg = 'Please fill out the entire form'
    else:
        msg = 'Please enter the following information in the fields below and click Add when done.'
    return render_template('addCustomerForm.html', msg=msg)

@app.route("/orderHistory", methods=['GET', 'POST'])
def orderHistory():
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    cursor.execute('SELECT * FROM OrderHistory INNER JOIN Cart ON Cart.OrderID=OrderHistory.OrderID;')
    connector.commit()
    cursor.execute('SELECT * FROM OrderHistory;')
    return render_template("orderHistory.html", data=cursor)
