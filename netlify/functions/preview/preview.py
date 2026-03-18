import sys, os
sys.path.insert(0, os.path.dirname(__file__))
# Reuse the preview_handler from the export module (engine.py lives alongside it)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'export'))
from export import preview_handler as handler
