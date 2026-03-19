import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'netlify', 'functions', 'export'))
from export import font_samples_handler as _netlify_handler
from _adapter import make_vercel_handler

handler = make_vercel_handler(_netlify_handler)
