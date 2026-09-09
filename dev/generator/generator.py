#!/usr/bin/env python3
"""
Script to generate 3DCSS from source image.
"""

import sys

if len(sys.argv) < 3:
    print("Usage: generator.py <url> <output> [<width>] [<height>]")
    sys.exit(1)
