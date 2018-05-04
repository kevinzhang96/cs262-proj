from crawler import Crawler
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

PORT_NUMBER = 80

crawler = Crawler()

class HandlerClass(BaseHTTPRequestHandler):
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self.wfile.write(str(crawler.dump('/home/kevinzhang/backup')))
    
    def do_HEAD(self):
        self._set_headers()

server = HTTPServer(('', PORT_NUMBER), HandlerClass)
server.serve_forever()