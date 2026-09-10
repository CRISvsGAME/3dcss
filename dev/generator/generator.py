#!/usr/bin/env python3
"""
Script to generate 3DCSS from source image.
"""

import sys
import re
import os
import urllib.parse

if len(sys.argv) < 3:
    print("Usage: generator.py <url> <output> [<width>] [<height>]")
    sys.exit(1)

URL, OUT = sys.argv[1], sys.argv[2]
WIDTH = sys.argv[3] if len(sys.argv) > 3 else None
HEIGHT = sys.argv[4] if len(sys.argv) > 4 else None


def generate_filename(url: str) -> str:
    """Generate Filename"""
    raw_path = urllib.parse.urlparse(url).path
    dec_path = urllib.parse.unquote(raw_path)
    raw_name = os.path.basename(dec_path)
    name, ext = os.path.splitext(raw_name)
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", name) or "source"
    safe_ext = re.sub(r"[^a-zA-Z0-9]", "", ext[1:])
    return f"{safe_name}.{safe_ext}" if safe_ext else safe_name
