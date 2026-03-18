# Label Maker

Type text, get a JEF embroidery file for your Janome machine. No BX fonts, no Embrilliance, no downloads — just type and go.

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser. Type your label, pick a font and color, click Generate, download the JEF.

## Command Line

```bash
# Single line
python label.py "Quilted by Carol"

# Multi-line label
python label.py "Just because —" "Quilted by Carol" "3-19-26"

# Options
python label.py "Hello" --font script --size 15 --color navy --output hello.jef

# Interactive mode
python label.py --interactive
```

## Fonts

| Name        | Style                        |
|-------------|------------------------------|
| script      | Flowing cursive (default)    |
| script2     | Lighter script               |
| sans        | Clean sans-serif             |
| serif       | Roman serif                  |
| serif-bold  | Bold serif                   |
| gothic      | Blackletter / gothic         |
| italic      | Italic serif                 |
| times       | Times-style serif            |
| times-bold  | Bold Times                   |

All fonts are Hershey vector fonts (public domain, designed by Dr. A.V. Hershey at the US Naval Weapons Laboratory in the 1960s).

## How It Works

1. **Hershey fonts** provide single-stroke vector paths for each character (public domain)
2. Each stroke is converted into a **satin column** — the engine computes perpendicular normals along the path and generates zigzag stitches between left and right rails
3. A **center-walk underlay** stabilizes the fabric before the top satin stitches
4. **pyembroidery** writes the stitch coordinates into a valid JEF file

## Settings

- **Height**: Letter height in mm (default 12mm, good for labels)
- **Satin width**: Column width in mm (default 1.2mm — thinner = more delicate, wider = bolder)
- **Density**: Stitch spacing along the path (default 0.35mm — lower = denser/slower, higher = lighter/faster)
- **Pull compensation**: Built-in 0.1mm extra width to offset thread tension

## Limitations

- These are stroke fonts, not filled fonts — letters are made of satin-stitched lines, not solid fills. This is intentional and matches how quality embroidery lettering works at small sizes.
- No automatic kerning adjustment beyond what the Hershey font data provides.
- Single color per label (the JEF is one color block).

## Files

- `engine.py` — Core text-to-stitch engine
- `label.py` — Command-line tool  
- `app.py` — Web interface (Flask)
- `requirements.txt` — Python dependencies
