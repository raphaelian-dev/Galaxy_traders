import sqlite3

class ParameterShouldNotBeNull(Exception):
    pass

class Products_database():
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
)
""")
        self.db.commit()
    def get_all_products(self):
        cursor = self.db.cursor()
        cursor.execute("""
SELECT * FROM products
""")
        products = cursor.fetchall()
        return products
    def get_all_products_HTML(self):
        HTML_code = ''
        products = self.get_all_products()
        for i in products:
            type_name = self.types[i[2]]
            name = i[0]
            HTML_code += '<div class="product '+type_name+'" onclick="openpopup(\''+i[4]+'\',\''+i[5]+'\',\''+type_name+'\')"><div class="properties-absolute"><div class="product-picture"><img src="./images/'+name+'.'+i[1]+'"><div class="price">'+str(i[3])+' STR</div></div><h3 class="product-title">'+name+'</h3><a class="more-info"></a></div></div>'
        return HTML_code
    def add_product(self, name:str, imageExtension:str, productType:int, price:int, description:str='We do not know much yet about this celestial body.', color:str='#808080'):
        if None in (name,productType,price) or productType>=len(self.types):
            raise ParameterShouldNotBeNull
        description = description.replace("'", "\\'")
        cursor = self.db.cursor()
        cursor.execute("""
INSERT INTO products (name, imageExtension, type, price, description, color)
VALUES ("""+str([name,imageExtension,productType,price,description,color])[1:-1].replace("\\\\'", "\\'")+""")
""")
        self.db.commit()
    def remove_product(self, name:str):
        cursor = self.db.cursor()
        cursor.execute("""
DELETE FROM products WHERE name='"""+name+"""'
""")
        self.db.commit()