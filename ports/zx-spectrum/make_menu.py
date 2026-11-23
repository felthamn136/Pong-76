#!/usr/bin/env python3
"""Generate Spectrum loading and menu screens and previews (requires Pillow)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PORT_DIR = Path(__file__).resolve().parent
FONT = PORT_DIR.parent.parent / "assets" / "Righteous-Regular.ttf"
def draw_banner(draw: ImageDraw.ImageDraw) -> None:
    title = ImageFont.truetype(str(FONT), 35)
    for y in (2, 6, 10, 14, 18):
        draw.line([(0, y), (64, y + 2), (128, y + 3),
                   (192, y + 2), (255, y)], fill=1)
    draw.rounded_rectangle((4, 25, 251, 75), radius=9, outline=1, width=2)
    draw.text((12, 27), "PONG'76", font=title, fill=1, stroke_width=0)
    draw.rounded_rectangle((207, 32, 243, 68), radius=5, outline=1, width=2)
    draw.rounded_rectangle((212, 39, 215, 61), radius=1, fill=1)
    draw.rounded_rectangle((235, 39, 238, 61), radius=1, fill=1)
    draw.rectangle((223, 48, 227, 52), fill=1)
    for y in (80, 84, 88, 92):
        draw.line([(0, y + 2), (64, y), (128, y - 1),
                   (192, y), (255, y + 2)], fill=1)


def banner_attributes() -> bytearray:
    attributes = bytearray([0x47] * 768)
    for row in (0, 1, 2, 10, 11):
        colour = 0x42 if row in (0, 2, 11) else 0x46
        attributes[row * 32:(row + 1) * 32] = bytes([colour]) * 32
    for row in range(3, 10):
        for col in (0, 1, 25, 26, 27, 28, 29, 30, 31):
            attributes[row * 32 + col] = 0x46
    return attributes


def write_screen(bitmap: Image.Image, attributes: bytearray, name: str) -> None:
    pixels = bytearray(6144)
    for y in range(192):
        for x in range(256):
            if bitmap.getpixel((x, y)):
                offset = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (x >> 3)
                pixels[offset] |= 0x80 >> (x & 7)
    (PORT_DIR / f"{name}.scr").write_bytes(pixels + attributes)

    palette = ((0, 0, 0), (0, 0, 205), (205, 0, 0), (205, 0, 205),
               (0, 205, 0), (0, 205, 205), (205, 205, 0), (205, 205, 205))
    preview = Image.new("RGB", (256, 192))
    for y in range(192):
        for x in range(256):
            attr = attributes[(y // 8) * 32 + x // 8]
            colour = (attr & 7) if bitmap.getpixel((x, y)) else ((attr >> 3) & 7)
            rgb = palette[colour]
            if attr & 0x40:
                rgb = tuple(255 if c else 0 for c in rgb)
            preview.putpixel((x, y), rgb)
    preview.save(PORT_DIR / f"{name}-preview.png")


def main() -> None:
    bitmap = Image.new("1", (256, 192))
    draw = ImageDraw.Draw(bitmap)
    draw_banner(draw)
    small = ImageFont.truetype(str(FONT), 10)
    draw.text((16, 102), "1 ONE PLAYER", font=small, fill=1)
    draw.text((136, 102), "2 TWO PLAYERS", font=small, fill=1)
    draw.text((16, 118), "3 SMALL PADDLE", font=small, fill=1)
    draw.text((136, 118), "4 LARGE PADDLE", font=small, fill=1)
    draw.text((16, 134), "5 SLOW", font=small, fill=1)
    draw.text((136, 134), "6 FAST", font=small, fill=1)
    draw.text((16, 150), "7 WHITE", font=small, fill=1)
    draw.text((136, 150), "8 GREEN", font=small, fill=1)
    draw.text((62, 182), "SPACE TO START", font=small, fill=1)
    attributes = banner_attributes()
    for row in (13, 15, 17, 19):
        attributes[row * 32 + 2:row * 32 + 16] = bytes([0x46]) * 14
        attributes[row * 32 + 17:row * 32 + 31] = bytes([0x07]) * 14
    write_screen(bitmap, attributes, "menu")

    bitmap = Image.new("1", (256, 192))
    draw = ImageDraw.Draw(bitmap)
    draw_banner(draw)
    body = ImageFont.truetype(str(FONT), 13)
    lines = (
        "An experimental build to see if",
        "Copilot AI could build a bong",
        "game in z80 machine code under",
        "the direction of a human!",
    )
    for row, line in enumerate(lines):
        x = round((256 - draw.textlength(line, font=body)) / 2)
        draw.text((x, 101 + row * 16), line, font=body, fill=1)
    loading = "LOADING..."
    x = round((256 - draw.textlength(loading, font=small)) / 2)
    draw.text((x, 178), loading, font=small, fill=1)
    attributes = banner_attributes()
    attributes[22 * 32:24 * 32] = bytes([0x46]) * 64
    write_screen(bitmap, attributes, "loading")


if __name__ == "__main__":
    main()
