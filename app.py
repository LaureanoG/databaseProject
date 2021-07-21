from flask import Flask, render_template, request, redirect, url_for, session
from random import seed, randint
import time
from datetime import date
import sqlite3

app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

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
        time.sleep(3)
        cursor.execute(i)
        connector.commit()
    return render_template("login.html", msg='Welcome to LLN Resto!')


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and request.form['username'] != "" and request.form['password'] != "":
        connector = sqlite3.connect('database.db')
        cursor = connector.cursor()
        username = request.form['username']
        password = request.form['password']
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
                # Use customer's password & username data to get customer ID
                cursor.execute("SELECT CustomerID FROM Customer WHERE Username = ? and Password = ?", \
                               (username, password))
                session['customerID'] = cursor.fetchone()[0]
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
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    file = open('initializeFoodItem.txt', 'r')
    for i in file.readlines():
        time.sleep(3)
        cursor.execute(i)
    connector.commit()
    return render_template('homeAdmin.html')


@app.route('/homeCustomer', methods=['GET', 'POST'])
def homeCustomer():
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    file = open('initializeFoodItem.txt', 'r')
    for i in file.readlines():
        time.sleep(3)
        cursor.execute(i)
    connector.commit()
    return render_template('homeCustomer.html')


@app.route("/cart", methods=['GET', 'POST'])
def cart():
    # Prints what is currently in the cart
    connector = sqlite3.connect('database.db', timeout = 10)
    cursor = connector.cursor()
    msg = 'NO'
    try:  # See if it exists
        session['price']
        session['orderID']
    except: # Initialize if non existent/start a new instance of cart
        session['price'] = 0
        seed(time.time())
        session['orderID'] = randint(0, 10000)
        for i in range(0, 6):
            cursor.execute('INSERT INTO Cart(?, ?, ?);', (session['OrderID'], i, 0))
            cursor.commit()
        cursor.execute('INSERT INTO OrderHistory(OrderID);', (session['orderID'],))

    if request.method == 'GET':
        food = request.args.get('food', None)
        msg = food + str(session['customerID'])
        # Increment item in cart table
        cursor.execute('SELECT Quantity FROM Cart NATURAL JOIN FoodItem WHERE OrderID = (?) AND Name = (?) AND Quantity IS NOT NULL', \
                        (session['orderID'], food))
        foodQuantity = cursor.fetchone()[0]
        # foodIDNum = cursor.execute('SELECT FoodID FROM FoodItem WHERE Name = (?)', (food,)).fetchone()
        # cursor.execute('UPDATE Cart SET Quantity = Quantity + 1 WHERE OrderID = (?) AND FoodID = (?)', (int(session['orderID']), foodIDNum))
        # #cursor.commit()
        # #session['price'] += cursor.execute('Select UnitPrice FROM FoodItem WHERE Name = (?)', (food,))
        # price = cursor.execute('SELECT Total FROM OrderHistory WHERE OrderID = (?);', (session['orderID'], ))
        # cursor.execute('UPDATE OrderHistory SET Total = (SELECT UnitPrice FROM FoodItem WHERE FoodID = (?)) + (?) WHERE OrderID = (?) and FoodID = (?);', (foodIDNum, price, session['orderID'], foodIDNum))
        # cursor.commit()
        # Maybe a dictionary would work well for storing values & food
    return render_template("cart.html", msg = msg)


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
    # When place order is clicked, CART TABLE  is emptied & order is added to table
    # if request.method == "POST":
    #     foodNames = {'Pizza': 1, 'Veggie Pizza': 2, 'Burger': 3}
    #     for x in foodNames:
    #         cursor.execute('INSERT INTO OrderHistory VALUES(?, ?, ?, ?, ?, ?)', \
    #                        (session['CustomerID'], randint(0, 100000), foodNames[x], session[x], date.today(), session['price']))
    #         connector.commit()
    cursor.execute('SELECT * FROM OrderHistory INNER JOIN Cart ON Cart.OrderID=OrderHistory.OrderID;')
    connector.commit()
    cursor.execute('SELECT * FROM OrderHistory;')
    return render_template("orderHistory.html", data=cursor)
