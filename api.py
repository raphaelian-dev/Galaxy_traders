import sqlite3

class Database():
    #
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
        self.db.commit()
    def get_all_products(self) -> list:
        cursor = self.db.cursor()
        cursor.execute("""
SELECT * FROM products ORDER BY price
""")
        products = cursor.fetchall()
        return products
    #
    def get_all_products_HTML(self) -> str:
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
        if None in (name,product_type,price) or product_type>=len(self.types):
            return False
        name = name.replace("'", "\\'")
        description = description.replace("'", "\\'")
        cursor = self.db.cursor()
        cursor.execute("""
INSERT INTO products (name, imageExtension, type, price, description, color)
VALUES ("""+str([name,imageExtension,product_type,price,description,color])[1:-1].replace("\\\\'", "\\'")+""")
""")
        self.db.commit()
    def remove_product(self, name:str):
        cursor = self.db.cursor()
        cursor.execute("""
DELETE FROM products WHERE name='"""+name+"""'
""")
        self.db.commit()
        return True
    #
    def add_order(self, product_name:str, email:str, name:str=None, first_name:str=None) -> bool:
        cursor = self.db.cursor()
        cursor.execute("""
SELECT * FROM products WHERE name='"""+product_name+"""'
""")
        product = cursor.fetchone()
        if not product:
            return False
        if None in (product_name, email):
            return False
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
    #
    def cancel_order(self, product_name:str):
        cursor = self.db.cursor()
        cursor.execute("""
SELECT  * FROM orders WHERE productName='"""+product_name+"""'
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
        