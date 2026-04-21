import sys, os, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'export'))
from export import handler as _handler
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self._send(_handler({'httpMethod': 'OPTIONS', 'body': ''}, {}))

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n).decode('utf-8') if n else ''
        self._send(_handler({'httpMethod': 'POST', 'body': body}, {}))

    def _send(self, result):
        status = result.get('statusCode', 200)
        body = result.get('body', '')
        is_b64 = result.get('isBase64Encoded', False)
        self.send_response(status)
        for k, v in result.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(base64.b64decode(body) if is_b64
                         else (body.encode() if isinstance(body, str) else body))
