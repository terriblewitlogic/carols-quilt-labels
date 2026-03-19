"""
Shared adapter: bridges Netlify-style handler(event, context) → Vercel BaseHTTPRequestHandler.
Import this in each api/*.py file.
"""
import base64
import os
import sys
from http.server import BaseHTTPRequestHandler

# Make the shared engine code importable from api/ files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'netlify', 'functions', 'export'))


def make_vercel_handler(netlify_handler):
    """Return a Vercel-compatible BaseHTTPRequestHandler class wrapping a Netlify handler."""

    class VercelHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # suppress default Apache-style logging

        def do_OPTIONS(self):
            result = netlify_handler({'httpMethod': 'OPTIONS', 'body': ''}, {})
            self._send(result)

        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length else ''
            result = netlify_handler({'httpMethod': 'POST', 'body': body}, {})
            self._send(result)

        def do_GET(self):
            result = netlify_handler({'httpMethod': 'GET', 'body': ''}, {})
            self._send(result)

        def _send(self, result):
            status = result.get('statusCode', 200)
            headers = result.get('headers', {})
            body = result.get('body', '')
            is_b64 = result.get('isBase64Encoded', False)

            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()

            if is_b64:
                self.wfile.write(base64.b64decode(body))
            else:
                self.wfile.write(body.encode('utf-8') if isinstance(body, str) else body)

    return VercelHandler
