from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        cur = mysql.connection.cursor()
        file = open('CreateTable.txt', 'r')
        for i in file.readlines():
            cur.execute(i)

    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route("/cart", methods=['GET', 'POST'])
def cart():
    return render_template("cart.html")

@app.route("/menu", methods=['GET', 'POST'])
def menu():
    return render_template("menu.html")

