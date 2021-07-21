from flask import Flask, render_template, request, redirect, url_for, session
from random import seed, randint
import time
from datetime import datetime
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
        time.sleep(1)
        cursor.execute(i)
        connector.commit()
    connector.close()
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
                connector.close()
                return render_template("homeCustomer.html")
        else:
            msg = 'The provided credentials do not match our records.\nPlease try again.'
            connector.close()
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
        time.sleep(1)
        cursor.execute(i)
    connector.commit()
    connector.close()
    return render_template('homeAdmin.html')


@app.route('/homeCustomer', methods=['GET', 'POST'])
def homeCustomer():
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    file = open('initializeFoodItem.txt', 'r')
    for i in file.readlines():
        time.sleep(1)
        cursor.execute(i)
    connector.commit()
    connector.close()
    return render_template('homeCustomer.html')


@app.route("/cart", methods=['GET', 'POST'])
def cart():
    # Prints what is currently in the cart
    connector = sqlite3.connect('database.db')
    cursor = connector.cursor()
    msg = 'NO'
    try:  # See if it exists
        session['price']
        session['orderID']
    except: # Initialize if non existent/start a new instance of cart
        msg = 'again'
        seed(time.time())
        session['orderID'] = randint(0, 10000)
    foodSet = {'Pizza', 'Veggie Pizza', 'Burger', 'Chicken Burger', 'Spaghetti', 'Chicken Alfredo'}
    if request.method == "GET" and request.args.get('food', None) not in foodSet:
        return render_template("cart.html", msg=msg)
    elif request.method == 'GET':
        food = request.args.get('food', None)
        #msg = food + " "+ str(session['orderID'])
        foodIDNum = cursor.execute('SELECT FoodID FROM FoodItem WHERE Name = (?);', (food,)).fetchone()[0]
        #msg += " " + str(foodIDNum)
        cursor.execute('INSERT INTO Cart VALUES(?, ?, ?);', (session['orderID'], foodIDNum, 1))
        connector.commit()
        cursor.execute('UPDATE OrderHistory SET Total = (SELECT UnitPrice FROM FoodItem WHERE FoodID = (?)) WHERE OrderID = (?) and FoodID = (?);', (foodIDNum, session['orderID'], foodIDNum))
        connector.commit()
    connector.close()
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
    #     foodNames = {'Pizza': 1, 'Veggie Pizza': 2, 'Burger': 3}
    #     for x in foodNames:
    #         cursor.execute('INSERT INTO OrderHistory VALUES(?, ?, ?, ?, ?, ?)', \
    #                        (session['CustomerID'], randint(0, 100000), foodNames[x], session[x], date.today(), session['price']))
    #         connector.commit()
    #cursor.execute('SELECT * FROM OrderHistory INNER JOIN Cart ON Cart.OrderID=OrderHistory.OrderID;')
    #connector.commit()

    if request.method == "GET":
        foodID = cursor.execute('SELECT FoodID FROM Cart WHERE OrderID = (?);', (session['orderID'], )).fetchone()[0]
        price = cursor.execute('SELECT UnitPrice FROM FoodItem WHERE FoodID = (?);', (foodID, )).fetchone()[0]
        cursor.execute('INSERT OR REPLACE INTO OrderHistory VALUES(?, ?, ?, ?, ?, ?);', \
                       (int(session['customerID']), int(session['orderID']), foodID, 1, datetime.today(), price))
        connector.commit()
        session['orderID'] = randint(0, 100000)
    fName = cursor.execute('SELECT Fname FROM Customer WHERE CustomerID = (?);', (int(session['customerID']),)).fetchone()[0]
    lName = cursor.execute('SELECT Lname FROM Customer WHERE CustomerID = (?);', (int(session['customerID']),)).fetchone()[0]
    cursor.execute('SELECT OrderID, FoodID, Quantity, Ordered, Total FROM OrderHistory ORDER BY Ordered;')
    return render_template("orderHistory.html", data=cursor, lname = lName, fname = fName)
