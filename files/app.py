#!/usr/bin/env python3
"""
Label Maker Web App — simple interface for generating JEF embroidery labels.
"""

import os
import uuid
import json
from flask import Flask, render_template_string, request, send_file, jsonify
from engine import (
    multiline_to_pattern, save_pattern, generate_preview_svg,
    available_fonts, FONT_ALIASES
)

app = Flask(__name__)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

THREAD_COLORS = {
    'Red':        '#cc0000',
    'Navy':       '#1a1a6b',
    'Black':      '#1a1a1a',
    'Forest':     '#1a5c1a',
    'Pink':       '#d4478a',
    'Purple':     '#6b2d8b',
    'Gold':       '#b8860b',
    'Orange':     '#cc5500',
    'Brown':      '#5c3317',
    'Teal':       '#1a7a7a',
    'Gray':       '#606060',
    'Burgundy':   '#700020',
}

# Hex string to int for pyembroidery
def hex_to_int(h):
    return int(h.lstrip('#'), 16)


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Label Maker</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f7f3ee;
    --card: #ffffff;
    --text: #2c2418;
    --muted: #8a7e6e;
    --accent: #b8432f;
    --accent-hover: #9c3726;
    --border: #e2dcd3;
    --input-bg: #faf8f5;
    --shadow: 0 1px 3px rgba(44,36,24,0.08), 0 4px 12px rgba(44,36,24,0.04);
  }
  
  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  body {
    font-family: 'DM Sans', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem 1rem;
  }
  
  .container {
    max-width: 640px;
    margin: 0 auto;
  }
  
  header {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  
  header h1 {
    font-family: 'Instrument Serif', serif;
    font-size: 2.4rem;
    font-weight: 400;
    letter-spacing: -0.02em;
    color: var(--text);
  }
  
  header p {
    color: var(--muted);
    font-size: 0.95rem;
    margin-top: 0.3rem;
  }
  
  .card {
    background: var(--card);
    border-radius: 12px;
    padding: 1.75rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
  }
  
  textarea {
    width: 100%;
    min-height: 110px;
    padding: 0.85rem 1rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    line-height: 1.6;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--input-bg);
    color: var(--text);
    resize: vertical;
    transition: border-color 0.2s;
  }
  textarea:focus {
    outline: none;
    border-color: var(--accent);
  }
  textarea::placeholder { color: #bbb3a5; }
  
  .row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1.25rem;
  }
  .row-3 { grid-template-columns: 1fr 1fr 1fr; }
  
  select, input[type="number"] {
    width: 100%;
    padding: 0.65rem 0.8rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--input-bg);
    color: var(--text);
    transition: border-color 0.2s;
  }
  select:focus, input:focus {
    outline: none;
    border-color: var(--accent);
  }
  
  .color-options {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  .color-swatch {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2.5px solid transparent;
    cursor: pointer;
    transition: border-color 0.15s, transform 0.15s;
    position: relative;
  }
  .color-swatch:hover { transform: scale(1.15); }
  .color-swatch.selected {
    border-color: var(--text);
    transform: scale(1.15);
  }
  .color-swatch::after {
    content: attr(title);
    position: absolute;
    bottom: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.65rem;
    color: var(--muted);
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.15s;
    pointer-events: none;
  }
  .color-swatch:hover::after { opacity: 1; }

  .btn {
    display: block;
    width: 100%;
    padding: 0.9rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #fff;
    background: var(--accent);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    margin-top: 1.5rem;
  }
  .btn:hover { background: var(--accent-hover); }
  .btn:active { transform: scale(0.99); }
  .btn:disabled {
    background: #c4b9aa;
    cursor: not-allowed;
  }
  
  #preview-area {
    margin-top: 1.5rem;
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    overflow: hidden;
  }
  #preview-area svg {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }
  #preview-area .placeholder {
    color: #c4b9aa;
    font-size: 0.9rem;
    font-style: italic;
  }
  
  .result-card {
    text-align: center;
    display: none;
  }
  .result-card.visible { display: block; }
  
  .result-info {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 1rem 0 1.25rem;
    font-size: 0.9rem;
    color: var(--muted);
  }
  .result-info span { font-weight: 600; color: var(--text); }
  
  .download-btn {
    display: inline-block;
    padding: 0.75rem 2rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
    background: var(--accent);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.2s;
  }
  .download-btn:hover { background: var(--accent-hover); }
  
  .spinner {
    display: none;
    width: 20px; height: 20px;
    border: 2.5px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    margin: 0 auto;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  
  footer {
    text-align: center;
    margin-top: 2rem;
    font-size: 0.8rem;
    color: var(--muted);
  }
</style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Label Maker</h1>
      <p>Type your text, pick a style, get a JEF file</p>
    </header>
    
    <div class="card">
      <label for="text-input">Label Text</label>
      <textarea id="text-input" placeholder="Just because —&#10;Quilted by Carol&#10;3-19-26" autofocus></textarea>
      
      <div class="row">
        <div>
          <label for="font-select">Font</label>
          <select id="font-select">
            {% for name in fonts %}
            <option value="{{ name }}" {% if name == 'script' %}selected{% endif %}>{{ name }}</option>
            {% endfor %}
          </select>
        </div>
        <div>
          <label for="size-input">Height (mm)</label>
          <input type="number" id="size-input" value="12" min="4" max="60" step="1">
        </div>
      </div>
      
      <div class="row">
        <div>
          <label for="align-select">Alignment</label>
          <select id="align-select">
            <option value="center" selected>Center</option>
            <option value="left">Left</option>
            <option value="right">Right</option>
          </select>
        </div>
        <div>
          <label for="width-input">Satin Width (mm)</label>
          <input type="number" id="width-input" value="1.2" min="0.5" max="3.0" step="0.1">
        </div>
      </div>
      
      <div style="margin-top: 1.25rem;">
        <label>Thread Color</label>
        <div class="color-options" id="color-options">
          {% for name, hex in colors.items() %}
          <div class="color-swatch {% if name == 'Red' %}selected{% endif %}" 
               style="background: {{ hex }};" 
               data-color="{{ hex }}" 
               title="{{ name }}"
               onclick="selectColor(this)"></div>
          {% endfor %}
        </div>
      </div>
      
      <button class="btn" id="generate-btn" onclick="generate()">
        <span id="btn-text">Generate Label</span>
        <div class="spinner" id="spinner"></div>
      </button>
    </div>
    
    <div class="card" id="preview-card">
      <label>Preview</label>
      <div id="preview-area">
        <span class="placeholder">Your label will appear here</span>
      </div>
    </div>
    
    <div class="card result-card" id="result-card">
      <label>Ready to Download</label>
      <div class="result-info">
        <div>Size: <span id="result-size"></span></div>
        <div>Stitches: <span id="result-stitches"></span></div>
      </div>
      <a class="download-btn" id="download-link" href="#">Download JEF</a>
    </div>
    
    <footer>
      Hershey vector fonts &middot; Public domain &middot; Satin stitch engine
    </footer>
  </div>

<script>
let selectedColor = '#cc0000';
let previewTimer = null;

function selectColor(el) {
  document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
  selectedColor = el.dataset.color;
  schedulePreview();
}

function getParams() {
  const text = document.getElementById('text-input').value.trim();
  return {
    text: text,
    font: document.getElementById('font-select').value,
    size: parseFloat(document.getElementById('size-input').value) || 12,
    align: document.getElementById('align-select').value,
    width: parseFloat(document.getElementById('width-input').value) || 1.2,
    color: selectedColor,
  };
}

function schedulePreview() {
  clearTimeout(previewTimer);
  previewTimer = setTimeout(updatePreview, 400);
}

async function updatePreview() {
  const params = getParams();
  if (!params.text) {
    document.getElementById('preview-area').innerHTML = 
      '<span class="placeholder">Your label will appear here</span>';
    return;
  }
  try {
    const resp = await fetch('/preview', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(params),
    });
    if (resp.ok) {
      const data = await resp.json();
      document.getElementById('preview-area').innerHTML = data.svg;
    }
  } catch(e) { /* ignore preview errors */ }
}

async function generate() {
  const params = getParams();
  if (!params.text) return;
  
  const btn = document.getElementById('generate-btn');
  const btnText = document.getElementById('btn-text');
  const spinner = document.getElementById('spinner');
  
  btn.disabled = true;
  btnText.style.display = 'none';
  spinner.style.display = 'block';
  
  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(params),
    });
    if (resp.ok) {
      const data = await resp.json();
      document.getElementById('result-size').textContent = data.size;
      document.getElementById('result-stitches').textContent = data.stitch_count;
      document.getElementById('download-link').href = '/download/' + data.filename;
      document.getElementById('result-card').classList.add('visible');
      
      // Also update preview
      document.getElementById('preview-area').innerHTML = data.svg;
    }
  } catch(e) {
    console.error(e);
  } finally {
    btn.disabled = false;
    btnText.style.display = 'inline';
    spinner.style.display = 'none';
  }
}

// Live preview on input changes
document.getElementById('text-input').addEventListener('input', schedulePreview);
document.getElementById('font-select').addEventListener('change', schedulePreview);
document.getElementById('size-input').addEventListener('change', schedulePreview);
document.getElementById('align-select').addEventListener('change', schedulePreview);
document.getElementById('width-input').addEventListener('change', schedulePreview);
</script>
</body>
</html>'''


@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        fonts=list(available_fonts().keys()),
        colors=THREAD_COLORS,
    )


@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    lines = [l for l in data['text'].split('\n') if l.strip()]
    if not lines:
        return jsonify({'svg': ''})
    
    svg = generate_preview_svg(
        lines,
        font_name=data.get('font', 'script'),
        height_mm=data.get('size', 12),
        align=data.get('align', 'center'),
        satin_width_mm=data.get('width', 1.2),
        thread_color=data.get('color', '#cc0000'),
    )
    return jsonify({'svg': svg})


@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    lines = [l for l in data['text'].split('\n') if l.strip()]
    if not lines:
        return jsonify({'error': 'No text'}), 400
    
    font_name = data.get('font', 'script')
    height_mm = data.get('size', 12)
    align = data.get('align', 'center')
    satin_width = data.get('width', 1.2)
    color_hex = data.get('color', '#cc0000')
    color_int = hex_to_int(color_hex)
    
    pattern = multiline_to_pattern(
        lines, font_name, height_mm,
        align=align,
        satin_width_mm=satin_width,
        thread_color=color_int,
    )
    
    # Save
    file_id = str(uuid.uuid4())[:8]
    slug = lines[0][:15].replace(' ', '_').replace('/', '-')
    filename = f'{slug}_{file_id}.jef'
    filepath = os.path.join(OUTPUT_DIR, filename)
    info = save_pattern(pattern, filepath)
    
    # Preview SVG
    svg = generate_preview_svg(
        lines, font_name, height_mm,
        align=align, satin_width_mm=satin_width,
        thread_color=color_hex,
    )
    
    return jsonify({
        'filename': filename,
        'size': f"{info['width_mm']:.0f} × {info['height_mm']:.0f} mm "
                f"({info['width_in']:.1f}\" × {info['height_in']:.1f}\")",
        'stitch_count': info['stitch_count'],
        'svg': svg,
    })


@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return 'Not found', 404
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    print("\n✂️  Label Maker running at http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
