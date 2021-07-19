from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
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
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
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
            msg = 'The provided credentials do not match our records.\nPlease try again.' + str(passwordDb)
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
    return render_template("cart.html")


@app.route("/menuCustomer", methods=['GET', 'POST'])
def menuCustomer():
    return render_template("menuCustomer.html")


@app.route("/menuAdmin", methods=['GET', 'POST'])
def menuAdmin():
    return render_template("menuAdmin.html")


@app.route("/orderHistory", methods=['GET', 'POST'])
def orderHistory():
    return render_template("orderHistory.html")


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return render_template("admin.html")
