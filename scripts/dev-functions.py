#!/usr/bin/env python3
"""
Local dev server that mimics Vercel /api/* function endpoints.
Usage: python3 scripts/dev-functions.py

Runs on port 9999. Vite proxies /api/* → http://localhost:9999/*
"""

import sys
import os

# Load .env from project root so GEMINI_API_KEY etc. are available
_root = os.path.join(os.path.dirname(__file__), '..')
_env_path = os.path.join(_root, '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())
    print(f'[functions] Loaded .env from {_env_path}')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'export'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'generate'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'image_to_jef'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'save_to_library'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'posterize'))

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64

# Import function handlers
import export as export_fn
import generate as generate_fn
import image_to_jef as image_to_jef_fn
import save_to_library as save_to_library_fn
import posterize as posterize_fn


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
            'export':           export_fn.handler,
            'preview':          export_fn.preview_handler,
            'font_samples':     export_fn.font_samples_handler,
            'generate':         generate_fn.handler,
            'image_to_jef':     image_to_jef_fn.handler,
            'save_to_library':  save_to_library_fn.handler,
            'posterize':        posterize_fn.handler,
        }
        fn = handlers.get(path)
        if not fn:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Function not found')
            return

        try:
            result = fn(event, {})
        except Exception as exc:
            import traceback
            tb = traceback.format_exc()
            print(f'[functions] EXCEPTION in /{path}:\n{tb}')
            result = {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': str(exc), 'traceback': tb}),
            }

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
    print('Available: /export  /preview  /font_samples  /generate  /image_to_jef  /save_to_library  /posterize')
    HTTPServer(('localhost', port), FunctionHandler).serve_forever()
