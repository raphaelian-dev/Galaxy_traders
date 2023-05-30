from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
import api
import threading
from sys import exit as sysexit

PORT = 8888

db = api.Database('Galaxy_traders')

class HTTPWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            content_types = {
    'html': 'text/html; charset=utf-8',
    'htm': 'text/html; charset=utf-8',
    'css': 'text/css',
    'js': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'ico': 'image/x-icon',
    'ttf': 'font/ttf'
}
            if '?' in self.path:
                self.path = self.path.split('?')[0]
            if '#' in self.path:
                self.path = self.path.split('#')[0]
            if self.path.startswith('/'):
                self.path='.'+self.path
            if self.path=='./':
                self.path='./index.html'
            if self.path == './api/getAllProductsHTML':
                all_products_HTML = db.get_all_products_HTML()
                self.send_response(200)
                self.send_header('content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(bytes(all_products_HTML, 'utf-8'))
                return
            elif not (self.path in ('./index.html','./products.html','./page_not_found.html',"connection.html",'./script.js','./style.css') or ((self.path.startswith('./assets/') or self.path.startswith('./images/')) and not self.path.endswith('/'))):
                raise FileNotFoundError
            content_type = content_types[self.path.split('.')[-1]]
            # Open the file
            with open(self.path, 'rb') as file:
                self.send_response(200)
                self.send_header('content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read()) # Read the file and send the contents
        except FileNotFoundError:
            self.send_response(301)
            self.send_header('Location','/page_not_found.html')
            self.end_headers()
    def do_POST(self):
        if '?' in self.path:
                self.path = self.path.split('?')[0]
        if '#' in self.path:
            self.path = self.path.split('#')[0]
        if self.path.startswith('/'):
            self.path='.'+self.path
        if self.path == './api/addOrder':
            try:
                args = self.rfile.read(int(self.headers.get('Content-Length'))).decode().split('\n')
                if db.add_order(*args):
                    self.send_response(204)
                else:
                    self.send_response(400)
            except TypeError:
                self.send_response(400)
            self.end_headers()
        elif self.path == './api/cancelOrder':
            product_name = self.rfile.read(int(self.headers.get('Content-Length'))).decode()
            db.cancel_order(product_name)
            self.send_response(204)
            self.end_headers()
        else:
            self.do_GET()


def stoping_thread_function():
    global httpd
    while input()!='exit':
        continue
    httpd.server_close()
    httpd.shutdown()
    sysexit()


httpd = TCPServer(("", PORT), HTTPWebHandler)

print("serving at port", PORT)

stoping_thread = threading.Thread(target=stoping_thread_function)
stoping_thread.start()
httpd.serve_forever()
sysexit()