#!/usr/bin/env python3
"""
Script to generate 3DCSS from source image.
"""

import json
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


def select_rectangles(img: Image.Image) -> list[Rectangle]:
    """Select Rectangles"""
    horizontal = extract_rectangles(img, "H")
    vertical = extract_rectangles(img, "V")
    if len(horizontal) <= len(vertical):
        return horizontal
    return vertical


def download_3dcss(dest: Path) -> None:
    """Download 3DCSS"""
    url = "https://api.github.com/repos/CRISvsGAME/3dcss/contents/src/css"
    request = urllib.request.Request(
        url, headers={"User-Agent": "3DCSS-Generator", "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        files = json.load(response)
    for file in files:
        if file["type"] == "file":
            download_source(file["download_url"], dest / "css" / file["name"])


def generate_palette(img: Image.Image, rectangles: list[Rectangle], dest: Path) -> None:
    """Generate Palette"""
    if img.mode != "P":
        raise ValueError("Image must be in palette mode")
    palette = img.getpalette()
    if palette is None:
        raise ValueError("Image must contain a colour palette")
    indices = sorted({rect.color_index for rect in rectangles})
    rules: list[str] = []
    for index in indices:
        offset = index * 3
        red, green, blue = palette[offset : offset + 3]
        rules.append(f".c{index} {{ background-color: rgb({red} {green} {blue}); }}")
    css = '@import "./css/index.css";\n' + "\n".join(rules) + "\n"
    css_file = dest / "main.css"
    css_file.write_text(css, encoding="utf-8")


def generate_grid(img: Image.Image, rectangles: list[Rectangle], dest: Path) -> None:
    """Generate Grid"""
    width, height = img.size
    col_starts = sorted({rect.x + 1 for rect in rectangles})
    row_starts = sorted({rect.y + 1 for rect in rectangles})
    col_spans = sorted({rect.width for rect in rectangles})
    row_spans = sorted({rect.height for rect in rectangles})
    rules = [
        ".image-viewport {",
        f"    --dcss-site-max: min(100%, calc(100dvh * {width} / {height}));",
        "    block-size: 100dvh;",
        "    align-items: center;",
        "}",
        ".image-grid {",
        f"    --dcss-col-tracks: repeat({width}, minmax(0, 1fr));",
        f"    --dcss-row-tracks: repeat({height}, minmax(0, 1fr));",
        f"    aspect-ratio: {width} / {height};",
        "}",
    ]
    for value in col_starts:
        rules.append(f".gx{value} {{ grid-column-start: {value}; }}")
    for value in row_starts:
        rules.append(f".gy{value} {{ grid-row-start: {value}; }}")
    for value in col_spans:
        rules.append(f".gw{value} {{ grid-column-end: span {value}; }}")
    for value in row_spans:
        rules.append(f".gh{value} {{ grid-row-end: span {value}; }}")
    css = "\n".join(rules) + "\n"
    css_file = dest / "main.css"
    with css_file.open("a", encoding="utf-8") as file:
        file.write(css)


def generate_html(rectangles: list[Rectangle], dest: Path) -> None:
    """Generate HTML"""
    html_file = dest / "index.html"

    with html_file.open("w", encoding="utf-8") as file:
        file.write("""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3DCSS Image</title>
    <link rel="stylesheet" href="main.css">
</head>
<body class="st image-viewport">
<div class="gr image-grid" role="img" aria-label="3DCSS Image">
""")
        for rect in rectangles:
            file.write(
                f'    <i class="c{rect.color_index} '
                f"gx{rect.x + 1} gy{rect.y + 1} "
                f'gw{rect.width} gh{rect.height}"></i>\n'
            )
        file.write("""</div>
</body>
</html>
""")


SRC = generate_filepath(URL, OUT)
download_source(URL, SRC)
image = load_image(SRC)
TARGET_WIDTH, TARGET_HEIGHT = calculate_dimensions(image, WIDTH, HEIGHT)
image = resize_image(image, TARGET_WIDTH, TARGET_HEIGHT)
image = quantize_image(image)
rects = select_rectangles(image)
download_3dcss(OUT)
generate_palette(image, rects, OUT)
generate_grid(image, rects, OUT)
generate_html(rects, OUT)
