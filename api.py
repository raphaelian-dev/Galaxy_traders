import sqlite3
import hashlib
from random import choices
from string import ascii_letters, digits, punctuation
characters = list(ascii_letters + digits + punctuation)
characters.remove("'")
from datetime import datetime, timedelta

class Database():
    # --- Creation or loading of the database
    def __init__(self, db_name:str):
        """Inits the python object. It has as a property a object which can be use to access the database located in the file of given name plus the .db extension. Creates if they do not exist the data tables for the products, the orders and the users."""
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
    hashedPassword CHAR(64) NOT NULL,
    name VARCHAR(50),
    firstName VARCHAR(50),
    permissionLevel INT DEFAULT 0,
    certified INT DEFAULT 0,
    hashedsession CHAR(64),
    sessiondate CHAR(14)
)
""")
        self.db.commit()
    # --- Operations on the products table of the database. ---
    def get_all_products(self) -> list:
        """Returns a list of tuples of all the properties of all the products, ordered by price."""
        cursor = self.db.cursor()
        cursor.execute("""
SELECT * FROM products ORDER BY price
""")
        products = cursor.fetchall()
        return products
    #
    def get_all_products_HTML(self) -> str:
        """Returns the HTML code usable for the products list in the website."""
        HTML_code = ''
        products = self.get_all_products()
        for i in products:
            type_name = self.types[i[2]]
            name = i[0]
            openpopup = 'onclick="openpopup(\''+i[4]+'\',\''+i[5]+'\',\''+type_name+'\')"'
            HTML_code += '<div class="product '+type_name+'"><div class="properties-absolute"><div class="product-picture"><img src="/images/'+name+'.'+i[1]+'" onclick="openOrderPopup(\''+name+'\')"><div class="price">'+str(i[3])+' STR</div></div><h3 class="product-title">'+name+'</h3><a class="more-info" '+openpopup+'></a></div></div>'
        return HTML_code
    #
    def add_product(self, name:str, imageExtension:str, product_type:int, price:int, description:str='We do not know much yet about this celestial body.', color:str='#808080') -> bool:
        """Registers a new product to the database. Returns True if operation successful, else False."""
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
    #
    def remove_product(self, name:str) -> None:
        """Removes a registered product from the database. Does not return anything, and does nothing if order does not exist."""
        cursor = self.db.cursor()
        cursor.execute("""
DELETE FROM products WHERE name='"""+name+"""'
""")
        self.db.commit()
    # --- Operations on the orders table of the database. ---
    def add_order(self, product_name:str, session:str) -> bool:
        """Registers an order to the database. Return True if operation successful, else False."""
        email = self.check_session(session)
        if type(email) == str:
            cursor = self.db.cursor()
            cursor.execute("SELECT name, firstName FROM users WHERE email='"+email+"'")
            name, first_name = cursor.fetchone()
            print(email, name, first_name)
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
        else:
            return False
    #
    def cancel_order(self, product_name:str) -> None:
        """Cancels an order registered in the database. Does not return anything, and does nothing if order does not exist."""
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
    def add_user(self, email:str, password:str, name:str|None=None, first_name:str|None=None) -> int:
        """Registers a user to the database. Returns -1 if no email or password given, 1 if user already exists or 0 if operation successful."""
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
    #
    def check_password(self, email:str, password:str) -> bool|None:
        """Returns None if user does not exist, else returns True if given password is correct for the user with given email, else False."""
        cursor = self.db.cursor()
        hashed_password = hash_password(password)
        cursor.execute("SELECT hashedPassword FROM users WHERE email='"+email+"'")
        real_hashed_tuple = cursor.fetchone()
        if real_hashed_tuple == None:
            return None
        return hashed_password == real_hashed_tuple[0]
    # --- Operations on user session
    def create_session(self, email:str) -> str:
        """Registers a user session identifiable by its 32 characters random ascii string. Returns the generated ID."""
        cursor = self.db.cursor()
        session = random_asciistr_32()
        hashedsession=hash_password(session)
        while cursor.execute("SELECT hashedsession FROM users WHERE hashedsession='"+hashedsession+"'").fetchone():
            session = random_asciistr_32()
            hashedsession = hash_password(session)
            print("Incredible coincidence !")
        cursor.execute("UPDATE users SET hashedsession='"+hashedsession+"',sessiondate='"+enddatestr()+"' WHERE email='"+email+"'")
        self.db.commit()
        return session
    #
    def connect_user(self, email:str, password:str) -> str|int:
        """Create a session for given user if the given password is correct. Returns 1 in case of wrong password, -1 if user does not exist, or else returns the generated session's ID."""
        password_correct = self.check_password(email, password)
        if password_correct:
            return self.create_session(email)
        elif password_correct == False:
            return 1
        else:
            return -1
    #
    def delete_session(self, session:str):
        """Deletes a user session. Does not return anything, and does nothing if session does not exist."""
        cursor = self.db.cursor()
        cursor.execute("UPDATE users SET hashedsession=NULL, sessiondate=NULL WHERE hashedsession='"+session+"'")
        self.db.commit()
    #
    def check_session(self, session:str) -> str|int:
        """Checks if user session is valid. Returns session user's email if so, or else if it is expired returns 1, otherwise -1."""
        cursor = self.db.cursor()
        session_attributes = cursor.execute("SELECT email, sessiondate FROM users WHERE hashedsession='"+hash_password(session)+"'").fetchone()
        if session_attributes == None:
            return -1
        email, sessiondate = session_attributes
        if int(sessiondate) < int(datestr()):
            self.delete_session(session)
            return 1
        return email


def hash_password(pswd:str) -> str:
    return hashlib.sha256(pswd.encode()).hexdigest()

def random_asciistr_32() -> str:
    return "".join(choices(characters, k=32))

def datestr() -> str:
    return str(datetime.today()).replace('-', '').replace(' ', '').replace(':', '').split('.')[0]

def enddatestr() -> str:
    return str(datetime.today()+timedelta(hours=24)).replace('-', '').replace(' ', '').replace(':', '').split('.')[0]
