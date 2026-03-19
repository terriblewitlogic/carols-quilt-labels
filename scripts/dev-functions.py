#!/usr/bin/env python3
"""
Local dev server that mimics Vercel /api/* function endpoints.
Usage: python3 scripts/dev-functions.py

Runs on port 9999. Vite proxies /api/* → http://localhost:9999/*
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'netlify', 'functions', 'export'))

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64

# Import the function handler
import export as export_fn


class FunctionHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f'[functions] {fmt % args}')

    def do_OPTIONS(self):
        self._dispatch({'httpMethod': 'OPTIONS', 'body': ''})

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else ''
        self._dispatch({'httpMethod': 'POST', 'body': body})

    def _dispatch(self, event):
        path = self.path.lstrip('/')
        handlers = {
            'export':        export_fn.handler,
            'preview':       export_fn.preview_handler,
            'font_samples':  export_fn.font_samples_handler,
        }
        fn = handlers.get(path)
        if not fn:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Function not found')
            return

        result = fn(event, {})
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


if __name__ == '__main__':
    port = 9999
    print(f'Local functions server running on http://localhost:{port}')
    print('Available: /export  /preview  /font_samples')
    HTTPServer(('localhost', port), FunctionHandler).serve_forever()
