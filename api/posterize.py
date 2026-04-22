import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'posterize'))
from posterize import handler as _handler
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send(_handler({'httpMethod': 'OPTIONS'}, {}))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length).decode('utf-8') if length else '{}'
        self._send(_handler({'httpMethod': 'POST', 'body': body}, {}))

    def _send(self, result):
        self.send_response(result.get('statusCode', 200))
        for k, v in result.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        body = result.get('body', '')
        self.wfile.write(body.encode('utf-8') if isinstance(body, str) else body)

    def log_message(self, *_):
        pass
