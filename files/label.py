#!/usr/bin/env python3
"""
Label Maker — Type text, get a JEF embroidery file.

Usage:
    python label.py "Just because"
    python label.py "Quilted by Carol" --font script --size 12
    python label.py "Line 1" "Line 2" "Line 3" --align center
    python label.py --interactive
"""

import argparse
import sys
import os
from datetime import date
from engine import (
    multiline_to_pattern, text_to_pattern, save_pattern, 
    available_fonts, get_text_width
)


THREAD_COLORS = {
    'red':      0xFF0000,
    'blue':     0x0000FF,
    'navy':     0x000080,
    'black':    0x000000,
    'green':    0x006400,
    'pink':     0xFF69B4,
    'purple':   0x800080,
    'gold':     0xDAA520,
    'orange':   0xFF8C00,
    'brown':    0x8B4513,
    'white':    0xFFFFFF,
    'gray':     0x808080,
}


def interactive_mode():
    """Walk Carol through making a label step by step."""
    print("\n✂️  Label Maker")
    print("=" * 40)
    
    # Get text
    print("\nType your label text. Press Enter twice when done:")
    lines = []
    while True:
        line = input("  > ")
        if line == "" and lines:
            break
        if line:
            lines.append(line)
    
    if not lines:
        print("No text entered. Bye!")
        return
    
    # Font choice
    fonts = available_fonts()
    print(f"\nFonts: {', '.join(fonts.keys())}")
    font_input = input(f"Font [{list(fonts.keys())[0]}]: ").strip()
    font_name = font_input if font_input in fonts else list(fonts.keys())[0]
    
    # Size
    size_input = input("Letter height in mm [12]: ").strip()
    try:
        height_mm = float(size_input) if size_input else 12.0
    except ValueError:
        height_mm = 12.0
    
    # Color
    print(f"Colors: {', '.join(THREAD_COLORS.keys())}")
    color_input = input("Thread color [red]: ").strip().lower()
    color = THREAD_COLORS.get(color_input, 0xFF0000)
    
    # Output filename
    default_name = lines[0][:20].replace(' ', '_').replace('/', '-')
    out_input = input(f"Output filename [{default_name}.jef]: ").strip()
    output = out_input if out_input else f"{default_name}.jef"
    if not output.endswith('.jef'):
        output += '.jef'
    
    # Generate
    print(f"\nGenerating '{output}'...")
    
    if len(lines) == 1:
        pattern, w, h = text_to_pattern(
            lines[0], font_name, height_mm,
            thread_color=color
        )
    else:
        pattern = multiline_to_pattern(
            lines, font_name, height_mm,
            align='center', thread_color=color
        )
    
    info = save_pattern(pattern, output)
    print_result(info)


def print_result(info):
    """Print a summary of the generated file."""
    print(f"\n✅ Done!")
    print(f"   File:     {info['jef_path']}")
    print(f"   Preview:  {info['png_path']}")
    print(f"   Size:     {info['width_mm']:.1f} × {info['height_mm']:.1f} mm "
          f"({info['width_in']:.1f}\" × {info['height_in']:.1f}\")")
    print(f"   Stitches: {info['stitch_count']}")


def main():
    parser = argparse.ArgumentParser(
        description="Label Maker — type text, get a JEF embroidery file."
    )
    parser.add_argument(
        'text', nargs='*',
        help='Label text. Multiple arguments = multiple lines.'
    )
    parser.add_argument(
        '-i', '--interactive', action='store_true',
        help='Interactive mode (step-by-step prompts)'
    )
    parser.add_argument(
        '-f', '--font', default='script',
        choices=list(available_fonts().keys()),
        help='Font name (default: script)'
    )
    parser.add_argument(
        '-s', '--size', type=float, default=12.0,
        help='Letter height in mm (default: 12)'
    )
    parser.add_argument(
        '-w', '--width', type=float, default=1.2,
        help='Satin column width in mm (default: 1.2)'
    )
    parser.add_argument(
        '-a', '--align', default='center',
        choices=['left', 'center', 'right'],
        help='Text alignment for multi-line labels (default: center)'
    )
    parser.add_argument(
        '-c', '--color', default='red',
        choices=list(THREAD_COLORS.keys()),
        help='Thread color (default: red)'
    )
    parser.add_argument(
        '-o', '--output', default=None,
        help='Output filename (default: auto-generated from text)'
    )
    parser.add_argument(
        '-d', '--density', type=float, default=0.35,
        help='Stitch density in mm (default: 0.35, lower = denser)'
    )
    
    args = parser.parse_args()
    
    if args.interactive or not args.text:
        interactive_mode()
        return
    
    lines = args.text
    color = THREAD_COLORS.get(args.color, 0xFF0000)
    
    # Auto-generate output name
    if args.output:
        output = args.output
    else:
        slug = lines[0][:20].replace(' ', '_').replace('/', '-')
        output = f"{slug}.jef"
    if not output.endswith('.jef'):
        output += '.jef'
    
    # Generate
    if len(lines) == 1:
        pattern, w, h = text_to_pattern(
            lines[0], args.font, args.size,
            satin_width_mm=args.width,
            density_mm=args.density,
            thread_color=color
        )
    else:
        pattern = multiline_to_pattern(
            lines, args.font, args.size,
            align=args.align,
            satin_width_mm=args.width,
            density_mm=args.density,
            thread_color=color
        )
    
    info = save_pattern(pattern, output)
    print_result(info)


if __name__ == '__main__':
    main()
