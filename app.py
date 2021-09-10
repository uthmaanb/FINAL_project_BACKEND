import sqlite3

import cloudinary.uploader
from flask import Flask, request
from flask_cors import CORS
from flask_mail import Mail, Message
import re


# This function create dictionaries out of SQL rows, so that the data follows JSON format
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# create user class
class User(object):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password


# create tables in sqlite
class CreateTable:

    def __init__(self):
        self.conn = sqlite3.connect('online_cafe.db')
        self.cursor = self.conn.cursor()

        # create admin table
        self.conn.execute("CREATE TABLE IF NOT EXISTS admin(admin_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "username TEXT NOT NULL, "
                          "first_name TEXT NOT NULL,"
                          "last_name TEXT NOT NULL,"
                          "cell TEXT NOT NULL,"
                          "email TEXT NOT NULL,"
                          "password TEXT NOT NULL)")
        print("users table created successfully")

        # user table
        self.conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "username TEXT NOT NULL, "
                          "first_name TEXT NOT NULL,"
                          "last_name TEXT NOT NULL,"
                          "cell TEXT NOT NULL,"
                          "email TEXT NOT NULL,"
                          "password TEXT NOT NULL,"
                          "address TEXT NOT NULL)")
        print("users table created successfully")

        # toppings / fillings table
        self.conn.execute("CREATE TABLE IF NOT EXISTS top_fil(top_fil_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                          "type TEXT NOT NULL,"
                          "description TEXT NOT NULL)")
        print("products table created successfully")

        # product table
        self.conn.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                          "image TEXT NOT NULL,"
                          "name TEXT NOT NULL,"
                          "prod_type TEXT NOT NULL,"
                          "description TEXT NOT NULL,"
                          "price TEXT NOT NULL)")
        print("products table created successfully")
        self.conn.close()


CreateTable()


# database functions
class Database(object):
    # function to connect to Database and create cursor
    def __init__(self):
        self.conn = sqlite3.connect('online_cafe.db')
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    # function for INSERT AND UPDATE query
    def insert(self, query, values):
        self.cursor.execute(query, values)
        self.conn.commit()

    # function to fetch data for SELECT query
    def fetch(self):
        return self.cursor.fetchall()

    # function for executing SELECT query
    def select(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def fetch1(self, query):
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchone()


# setting up API
app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

# email tings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cody01101101@gmail.com'
app.config['MAIL_PASSWORD'] = 'pqqcaclgnoebgnnx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


# using cloudinary to upload images to database
def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(
        cloud_name="pizzaboii96",
        api_key="811499535753334",
        api_secret="6jOJ_zBk9zetHIcM-g8enLSmuMQ"
    )
    # upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        image = request.json['image']
        app.logger.info('%s file_to_upload', image)
        if image:
            upload_result = cloudinary.uploader.upload(image)
            app.logger.info(upload_result)
            return upload_result['url']


# x x   x   x   x   x   x   x   xx  xx  x   xx      xx  xx  xx      xx      xx  xx  xx  xx  xx  x   x   xx  x   xx  xx
# admin functions
@app.route('/admin/', methods=["POST", "GET", "PATCH"])
def admin_fx():
    response = {}
    db = Database()

    # Register function
    if request.method == "POST":
        try:
            username = request.json['username']
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            cell = request.json['cell']
            email = request.json['email']
            password = request.json['password']

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

            if re.search(regex, email):
                query = ("INSERT INTO admin("
                         "username,"
                         "first_name,"
                         "last_name,"
                         "cell, "
                         "email,"
                         "password) VALUES(?, ?, ?, ?, ?, ?)")
                values = username, first_name, last_name, cell, email, password
                db.insert(query, values)

                msg = Message('You\'ve been registered as an admin', sender='cody01101101@gmail.com',
                              recipients=[email])
                msg.body = "Thank You " + first_name + ", we hope you enjoy your stay"
                mail.send(msg)
                response["message"] = "successfully added new admin to database"
                response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 209

        return response

    # Login function
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        query = f"SELECT * FROM admin WHERE username='{username}' AND password='{password}'"
        db.select(query)
        user = db.fetch1(query)

        response['status_code'] = 200
        response['message'] = 'admin user logged in'
        response['data'] = user

        return response

    # Fetches ALL users in users table
    if request.method == "GET":
        query = "SELECT * FROM  admin"
        db.select(query)

        response['status_code'] = 200
        response['data'] = db.fetch()
        return response


# edit admin
@app.route('/edit-admin/<int:admin_id>', methods=["PUT"])
def edit_admin(admin_id):
    response = {}
    db = Database()

    if request.method == "PUT":
        try:
            username = request.json['username']
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            cell = request.json['cell']
            email = request.json['email']
            password = request.json['password']

            query = ("UPDATE admin SET username=?,"
                     "first_name=?,"
                     "last_name=?,"
                     "cell=?,"
                     "email=?,"
                     "password=?"
                     "WHERE admin_id=?")
            values = username, first_name, last_name, cell, email, password, admin_id
            db.insert(query, values)

            response["message"] = "user was successfully updated"
            response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed to update user"
            response["status_code"] = 209

        return response


# delete admin from table
@app.route("/delete-admin/<int:admin_id>")
def delete_admin(admin_id):

    response = {}
    db = Database()

    query = "DELETE FROM admin WHERE admin_id=" + str(admin_id)
    db.select(query)

    # check if the id exists
    if not id:
        return "user does not exist"

    else:
        response['status_code'] = 200
        response['message'] = "item deleted successfully."
        return response


#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x
# user app route for functions
@app.route('/users/', methods=["POST", "GET", "PATCH"])
def user_fx():
    response = {}
    db = Database()

    # Register function
    if request.method == "POST":
        try:
            username = request.json['username']
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            cell = request.json['cell']
            email = request.json['email']
            password = request.json['password']
            address = request.json['address']

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

            if re.search(regex, email):
                query = ("INSERT INTO users("
                         "username,"
                         "first_name,"
                         "last_name,"
                         "cell, "
                         "email,"
                         "password,"
                         "address) VALUES(?, ?, ?, ?, ?, ?, ?)")
                values = username, first_name, last_name, cell, email, password, address
                db.insert(query, values)

                msg = Message('We welcome you to Cafe Breda', sender='cody01101101@gmail.com', recipients=[email])
                msg.body = "Thank You " + first_name + ", we appreciate your support!"
                mail.send(msg)
                response["message"] = "successfully added new user to database"
                response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 209

        return response

    # Login function
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        db.select(query)

        response['status_code'] = 200
        response['data'] = db.fetch1(query)
        return response

    # Fetches ALL users in users table
    if request.method == "GET":
        query = "SELECT * FROM  users"
        db.select(query)

        response['status_code'] = 200
        response['data'] = db.fetch()
        return response


# edit users
@app.route('/edit-user/<int:user_id>', methods=["PUT", "GET"])
def edit_user(user_id):
    response = {}
    db = Database()

    if request.method == "PUT":
        try:
            username = request.json['username']
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            cell = request.json['cell']
            email = request.json['email']
            password = request.json['password']
            address = request.json['address']

            query = ("UPDATE users SET username=?,"
                     "first_name=?,"
                     "last_name=?,"
                     "cell=?,"
                     "email=?,"
                     "password=?,"
                     "address=?"
                     "WHERE user_id=?")
            values = username, first_name, last_name, cell, email, password, address, user_id
            db.insert(query, values)

            response["message"] = "user was successfully updated"
            response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed to update user"
            response["status_code"] = 209

        return response

    if request.method == "GET":
        query = f"SELECT * FROM  users WHERE user_id='{user_id}'"
        db.fetch1(query)

        response['status_code'] = 200
        response['data'] = db.fetch1(query)
        return response


# delete user from table
@app.route("/delete-users/<int:user_id>")
def delete_users(user_id):

    response = {}
    db = Database()

    query = "DELETE FROM users WHERE user_id=" + str(user_id)
    db.select(query)

    # check if the id exists
    if not id:
        return "user does not exist"

    else:
        response['status_code'] = 200
        response['message'] = "item deleted successfully."
        return response


#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x
# product functions
@app.route('/products/', methods=["POST", "GET"])
def product_fx():
    response = {}
    db = Database()

    # product Register function
    if request.method == "POST":
        try:
            image = upload_file()
            name = request.json['name']
            prod_type = request.json['prod_type']
            description = request.json['description']
            price = request.json['price']

            query = ("INSERT INTO products("
                     "image,"
                     "name,"
                     "prod_type,"
                     "description,"
                     "price) VALUES(?, ?, ?, ?, ?)")
            values = image, name, prod_type, description, price
            db.insert(query, values)

            response["message"] = "successfully added new product to database"
            response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 209

        return response

    # Fetches ALL products in products table
    if request.method == "GET":
        query = "SELECT * FROM  products"
        db.select(query)

        response['status_code'] = 200
        response['data'] = db.fetch()
        return response


# edit products
@app.route('/edit-product/<int:prod_id>', methods=["PUT"])
def edit_product(prod_id):
    response = {}
    db = Database()

    if request.method == "PUT":
        try:
            image = request.json['image']
            name = request.json['name']
            prod_type = request.json['prod_type']
            description = request.json['description']
            price = request.json['price']

            query = ("UPDATE products SET image=?,"
                     "name=?,"
                     "prod_type=?,"
                     "description=?,"
                     "price=?"
                     "WHERE prod_id=?")
            values = image, name, prod_type, description, price, prod_id
            db.insert(query, values)

            response["message"] = "Product was successfully updated"
            response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed to update product"
            response["status_code"] = 209

        return response


# delete products from table
@app.route("/delete-products/<int:prod_id>")
def delete_products(prod_id):

    response = {}
    db = Database()

    query = "DELETE FROM products WHERE prod_id=" + str(prod_id)
    db.select(query)

    # check if the id exists
    if not id:
        return "product does not exist"

    else:
        response['message'] = "item deleted successfully."
        response['status_code'] = 200
        return response


# x x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x
# top_fil functions
@app.route('/top_fil/', methods=["POST", "GET"])
def top_fil_fx():
    response = {}
    db = Database()

    # topping/filling Register function
    if request.method == "POST":
        try:
            top_fil = request.json['type']
            description = request.json['description']

            query = ("INSERT INTO top_fil("
                     "type,"
                     "description) VALUES(?, ?)")
            values = top_fil, description
            db.insert(query, values)

            response["message"] = "successfully added new product to database"
            response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 209

        return response

    # Fetches ALL products in products table
    if request.method == "GET":
        query = "SELECT * FROM  top_fil"
        db.select(query)

        response['status_code'] = 200
        response['data'] = db.fetch()
        return response


# edit top_fil
@app.route('/edit-top_fil/<int:top_fil_id>', methods=["PUT"])
def edit_top_fil(top_fil_id):
    response = {}
    db = Database()

    if request.method == "PUT":
        try:
            description = request.json['description']
            top_fil_type = request.json['type']

            query = ("UPDATE top_fil SET type=?,"
                     "description=?"
                     "WHERE top_fil_id=?")
            values = top_fil_type, description, top_fil_id
            db.insert(query, values)

            response["message"] = "topping/filling was successfully updated"
            response["status_code"] = 201

        except ValueError:
            response["message"] = "Failed to update topping/filling"
            response["status_code"] = 209

        return response


# delete toppings/fillings from table
@app.route("/delete-top_fil/<int:top_fil_id>")
def delete_top_fil(top_fil_id):

    response = {}
    db = Database()

    query = "DELETE FROM top_fil WHERE top_fil_id=" + str(top_fil_id)
    db.select(query)

    # check if the id exists
    if not id:
        return "product does not exist"

    else:
        response['message'] = "item deleted successfully."
        response['status_code'] = 200
        return response


if __name__ == '__main__':
    app.run(debug=True)
