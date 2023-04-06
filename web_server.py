from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
import api
import threading


PORT = 8888


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
            if self.path.startswith('/'):
                self.path='.'+self.path
            if self.path=='./':
                self.path='./index.html'
            if self.path == './api/getAllProductsHTML':
                db = api.Products_database('products')
                self.send_response(200)
                self.send_header('content-type', 'text/html; charset=utf-8')
                self.end_headers()
                all_products_HTML = db.get_all_products_HTML()  
                self.wfile.write(bytes(all_products_HTML, 'utf-8'))
                return
            elif not (self.path in ('./index.html','./products.html','./page_not_found.html','./script.js','./style.css') or ((self.path.startswith('./assets/') or self.path.startswith('./images/')) and not self.path.endswith('/'))):
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
        return self.do_GET()


def stoping_thread_function():
    global httpd
    while input()!='exit':
        continue
    httpd.server_close()
    httpd.shutdown()


httpd = TCPServer(("", PORT), HTTPWebHandler)

print("serving at port", PORT)

stoping_thread = threading.Thread(target=stoping_thread_function)
stoping_thread.start()
httpd.serve_forever()