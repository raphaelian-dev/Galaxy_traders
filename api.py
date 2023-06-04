import sqlite3
import hashlib
from random import choices
from string import ascii_letters, digits, punctuation
characters = list(ascii_letters + digits + punctuation)
characters.remove("'")
from datetime import date

class Database():
    # Inits the python object. It has as a property a object which can be use to access the database located in the file of given name plus the .db extension. Creates if they do not exist the data tables for the products, the orders and the users.
    def __init__(self, db_name:str):
        self.types=('inhabitable-planet','not-inhabitable-planet','moon','star-in-system','star-without-system')
        self.db = sqlite3.connect('./data/'+db_name+'.db')
        cursor = self.db.cursor()
        cursor.execute("""
CREATE TABLE IF NOT EXISTS products
(
    name VARCHAR(22) PRIMARY KEY NOT NULL,
    imageExtension VARCHAR(4) NOT NULL,
    type INT NOT NULL,
    price INT NOT NULL,
    description TEXT DEFAULT 'We do not know much yet about this celestial body.',
    color CHAR(6) DEFAULT '#808080'
)""")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS orders
(
    productName VARCHAR(22) PRIMARY KEY NOT NULL,
    email VARCHAR(320) NOT NULL,
    name VARCHAR(50),
    firstName VARCHAR(50),
    imageExtension VARCHAR(4) NOT NULL,
    type INT NOT NULL,
    price INT NOT NULL,
    description TEXT DEFAULT 'We do not know much yet about this celestial body.',
    color CHAR(6) DEFAULT '#808080'
)
""")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS users
(
    email VARCHAR(320) PRIMARY KEY NOT NULL,
    hashedPassword VARCHAR(32) NOT NULL,
    name VARCHAR(50),
    firstName VARCHAR(50),
    permissionLevel INT DEFAULT 0,
    certified INT DEFAULT 0,
    session VARCHAR(32),
    sessiondate CHAR(7)
)
""")
        self.db.commit()
    def get_all_products(self) -> list:
        cursor = self.db.cursor()
        cursor.execute("""
SELECT * FROM products ORDER BY price
""")
        products = cursor.fetchall()
        return products
    # Returns the HTML code usable for the products list in the website.
    def get_all_products_HTML(self) -> str:
        HTML_code = ''
        products = self.get_all_products()
        for i in products:
            type_name = self.types[i[2]]
            name = i[0]
            openpopup = 'onclick="openpopup(\''+i[4]+'\',\''+i[5]+'\',\''+type_name+'\')"'
            HTML_code += '<div class="product '+type_name+'"><div class="properties-absolute"><div class="product-picture"><img src="/images/'+name+'.'+i[1]+'" onclick="openOrderPopup(\''+name+'\')"><div class="price">'+str(i[3])+' STR</div></div><h3 class="product-title">'+name+'</h3><a class="more-info" '+openpopup+'></a></div></div>'
        return HTML_code
    # --- Operations on the products table of the database. ---
    # Registers a new product to the database. Returns True if operation successful, else False.
    def add_product(self, name:str, imageExtension:str, product_type:int, price:int, description:str='We do not know much yet about this celestial body.', color:str='#808080') -> bool:
        if None in (name,product_type,price) or '' in (name,product_type,price) or product_type>=len(self.types):
            return False
        name = name.replace("'", "\\'")
        description = description.replace("'", "\\'")
        cursor = self.db.cursor()
        cursor.execute("""
INSERT INTO products (name, imageExtension, type, price, description, color)
VALUES ("""+str([name,imageExtension,product_type,price,description,color])[1:-1].replace("\\\\'", "\\'")+""")
""")
        self.db.commit()
        return True
    # Removes a registered product from the database.
    def remove_product(self, name:str):
        cursor = self.db.cursor()
        cursor.execute("""
DELETE FROM products WHERE name='"""+name+"""'
""")
        self.db.commit()
        return True
    # --- Operations on the orders table of the database. ---
    # Registers an order to the database. Return True if operation successful, else False.
    def add_order(self, product_name:str, email:str, name:str|None=None, first_name:str|None=None) -> bool:
        cursor = self.db.cursor()
        cursor.execute("""
SELECT * FROM products WHERE name='"""+product_name+"""'
""")
        product = cursor.fetchone()
        if not product:
            return False
        if None in (product_name, email) or '' in (product_name, email):
            return False
        email = email.replace('%40', '@')
        keys = 'productName, email, imageExtension, type, price, description, color'
        values = [product_name, email]+list(product[1:])
        if name != None:
            keys += ', name'
            values.append(name)
        if first_name!=None:
            keys += ', firstName'
            values.append(first_name)

        cursor = self.db.cursor()
        cursor.execute("""
INSERT INTO orders ("""+keys+""")
VALUES ("""+str(values)[1:-1]+""")
""")
        self.db.commit()
        self.remove_product(product_name)
        return True
    # Cancels an order registered in the database.
    def cancel_order(self, product_name:str):
        cursor = self.db.cursor()
        cursor.execute("""
SELECT productName, imageExtension, type, price, description, color FROM orders WHERE productName='"""+product_name+"""'
""")
        product = cursor.fetchone()
        if not product:
            return
        product = list(product)
        product[4] = product[4].replace('\\','')
        product[0] = product[0].replace('\\','')
        self.add_product(*product)
        cursor.execute("""
DELETE FROM orders WHERE productName='"""+product_name+"""'
""")
        self.db.commit()
    # --- Operations on the users table of the database. ---
    # Registers a user to the database. Returns -1 if no email or password given, 1 if user already exists or 0 if operation successful.
    def add_user(self, email:str, password:str, name:str|None=None, first_name:str|None=None) -> int:
        cursor = self.db.cursor()
        if None in (email, password) or '' in (email, password):
            return -1
        cursor.execute("SELECT email FROM users WHERE email='"+email+"'")
        if cursor.fetchone():
            return 1
        hashed_password = hash_password(password)
        keys = 'email, hashedPassword'
        values = [email, hashed_password]
        if name != None:
            keys += ', name'
            values.append(name)
        if first_name!=None:
            keys += ', firstName'
            values.append(first_name)
        cursor.execute("""
INSERT INTO users ("""+keys+""")
VALUES ("""+str(values)[1:-1]+""")
""")
        self.db.commit()
        return 0
    # Returns None if user does not exist, else returns True if given password is correct for the user with given email, else False.
    def check_password(self, email:str, password:str) -> bool|None:
        cursor = self.db.cursor()
        hashed_password = hash_password(password)
        cursor.execute("SELECT hashedPassword FROM users WHERE email='"+email+"'")
        real_hashed_tuple = cursor.fetchone()
        if real_hashed_tuple == None:
            return None
        return hashed_password == real_hashed_tuple[0]
    # TODO : Hash of sessions. PS : hash is 32*16 and sessions' IDs are 32*93.
    # Registers a user session identifiable by its 32 characters random ascii string. Returns the generated ID.
    def create_session(self, email:str) -> str:
        cursor = self.db.cursor()
        session = random_asciistr_32()
        while cursor.execute("SELECT session FROM users WHERE session='"+session+"'").fetchone():
            session = random_asciistr_32()
            print("Incredible coincidence !")
        cursor.execute("UPDATE users SET session='"+session+"',sessiondate='"+datestr()+"' WHERE email='"+email+"'")
        self.db.commit()
        return session
    # Create a session for given user if the given password is correct. Returns 1 in case of wrong password, -1 if user does not exist, or else returns the generated session's ID.
    def connect_user(self, email:str, password:str) -> str|int:
        password_correct = self.check_password(email, password)
        if password_correct:
            return self.create_session(email)
        elif password_correct == False:
            return 1
        else:
            return -1
    # Deletes a user session.
    def delete_session(self, session:str):
        cursor = self.db.cursor()
        cursor.execute("UPDATE users SET session=NULL, sessiondate=NULL WHERE session='"+session+"'")
        self.db.commit()
    # Checks if user session is valid. Returns session user's email if so, else if it is just expired "expired", else None.
    def check_session(self, session:str) -> str|None:
        cursor = self.db.cursor()
        session_attributes = cursor.execute("SELECT email, sessiondate FROM users WHERE session='"+session+"'").fetchone()
        if session_attributes == None:
            return None
        email, sessiondate = session_attributes
        if sessiondate != datestr():
            self.delete_session(session)
            return 'expired'
        return email


def hash_password(pswd:str) -> str:
    return hashlib.sha256(pswd.encode()).hexdigest()

def random_asciistr_32() -> str:
    return "".join(choices(characters, k=32))

def datestr() -> str:
    return str(date.today()).replace('-','')
