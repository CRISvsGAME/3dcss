#!/usr/bin/env python3
"""
Script to generate 3DCSS from source image.
"""

import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast
from PIL import Image, ImageOps

if len(sys.argv) < 3:
    print("Usage: generator.py <url> <output> [<width>] [<height>]")
    sys.exit(1)


@dataclass(slots=True)
class Rectangle:
    """Reactangle"""

    x: int
    y: int
    width: int
    height: int
    color_index: int


URL = sys.argv[1]
OUT = Path(sys.argv[2]).expanduser()
WIDTH = int(sys.argv[3]) if len(sys.argv) > 3 else 0
HEIGHT = int(sys.argv[4]) if len(sys.argv) > 4 else 0


def generate_filepath(url: str, dest: Path) -> Path:
    """Generate Filepath"""
    raw_path = urllib.parse.urlparse(url).path
    dec_path = urllib.parse.unquote(raw_path)
    raw_name = os.path.basename(dec_path)
    name, ext = os.path.splitext(raw_name)
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", name) or "source"
    safe_ext = re.sub(r"[^a-zA-Z0-9]", "", ext[1:])
    filename = f"{safe_name}.{safe_ext}" if safe_ext else safe_name
    return dest / filename


def download_source(url: str, dest: Path) -> None:
    """Download Source"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "3DCSS-Generator"})
    with urllib.request.urlopen(request, timeout=10) as response:
        with open(dest, "wb") as file:
            shutil.copyfileobj(response, file)


def load_image(src: Path) -> Image.Image:
    """Load Image"""
    with Image.open(src) as src_img:
        return src_img.convert("RGB")


def calculate_dimensions(img: Image.Image, width: int, height: int) -> tuple[int, int]:
    """Calculate Dimensions"""
    src_width, src_height = img.size
    if width < 0 or height < 0:
        raise ValueError("Width and height must be positive")
    if width == 0 and height == 0:
        return src_width, src_height
    if width == 0:
        return max(1, round(src_width * height / src_height)), height
    if height == 0:
        return width, max(1, round(src_height * width / src_width))
    return width, height


def resize_image(img: Image.Image, width: int, height: int) -> Image.Image:
    """Resize Image"""
    if img.size == (width, height):
        return img
    return ImageOps.fit(img, (width, height), method=Image.Resampling.LANCZOS)


def quantize_image(img: Image.Image, colors: int = 256) -> Image.Image:
    """Quantize Image"""
    return img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)


# pylint: disable=too-many-locals
def extract_rectangles(
    img: Image.Image, orientation: Literal["H", "V"]
) -> list[Rectangle]:
    """Extract Rectangles"""
    if img.mode != "P":
        raise ValueError("Image must be in palette mode")
    if orientation not in ("H", "V"):
        raise ValueError("Orientation must be 'H' or 'V'")
    horizontal = orientation == "H"
    width, height = img.size
    number_of_lines = height if horizontal else width
    length_of_line = width if horizontal else height
    rectangles: list[Rectangle] = []
    active: dict[tuple[int, int, int], Rectangle] = {}
    for line in range(number_of_lines):
        position = 0
        next_active: dict[tuple[int, int, int], Rectangle] = {}
        while position < length_of_line:
            start = position
            x, y = (position, line) if horizontal else (line, position)
            color_index = cast(int, img.getpixel((x, y)))
            position += 1
            while position < length_of_line:
                x, y = (position, line) if horizontal else (line, position)
                if img.getpixel((x, y)) != color_index:
                    break
                position += 1
            length = position - start
            key = (start, length, color_index)
            rect = active.pop(key, None)
            if rect is None:
                if horizontal:
                    rect = Rectangle(start, line, length, 1, color_index)
                else:
                    rect = Rectangle(line, start, 1, length, color_index)
            elif horizontal:
                rect.height += 1
            else:
                rect.width += 1
            next_active[key] = rect
        rectangles.extend(active.values())
        active = next_active
    rectangles.extend(active.values())
    return rectangles


SRC = generate_filepath(URL, OUT)
download_source(URL, SRC)
image = load_image(SRC)
TARGET_WIDTH, TARGET_HEIGHT = calculate_dimensions(image, WIDTH, HEIGHT)
image = resize_image(image, TARGET_WIDTH, TARGET_HEIGHT)
image = quantize_image(image)
