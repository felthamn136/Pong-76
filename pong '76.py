import tkinter as tk
import tkinter.font as tkfont

# Window Rendering
# This section sets up the main application window with a 4:3 aspect ratio and a black background.

root = tk.Tk()
root.title("Pong '76")
root.geometry("800x600")
root.resizable(True, True)
root.configure(bg="black")
root.wm_aspect(4, 3, 4, 3)

# Scanline Rendering
# This section draws alternating near-black scanlines to simulate a CRT display.
# CRT scanline note: 240p (or 224 active lines) maps to alternating active
# and black pixel rows at 480p output.
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Attraction Logo
# Draws smooth, centered title lettering along a shallow arc and scales it with the window.
logo_text = "PONG '76"
logo_font = tkfont.Font(root=root, family="Helvetica", size=72, weight="bold")

# Attraction Description
# Places the game's background and development note beneath the logo.
description_text = (
    "This experimental Copilot AI-developed game is inspired by the classic Squash game "
    "found on late-1970s Grandstand TV gaming consoles, including the Adman Grandstand "
    "3000 and Video Sports Centre 6000 Colour. The project was created through a series "
    "of carefully engineered prompts designed by Neil Feltham to explore the "
    "capabilities of modern AI-assisted game development."
)
description_font = tkfont.Font(root=root, family="Helvetica", size=16)

def draw_logo(event):
    canvas.delete("logo")
    logo_font.configure(size=max(24, int(event.width * 0.09)))
    widths = [logo_font.measure(character) for character in logo_text]
    text_width = sum(widths)
    x = (event.width - text_width) / 2
    half_width = text_width / 2
    baseline = event.height * 0.24
    arc_height = min(16, event.height * 0.025)

    for character, width in zip(logo_text, widths):
        center_x = x + width / 2
        curve_position = (center_x - event.width / 2) / half_width
        y = baseline + arc_height * curve_position**2
        canvas.create_text(
            center_x,
            y,
            text=character,
            font=logo_font,
            fill="#f4e8c1",
            tags="logo",
        )
        x += width

def draw_description(event):
    canvas.delete("description")
    description_font.configure(size=max(12, int(event.width * 0.02)))
    max_width = event.width * 0.78
    lines = []
    current_line = ""
    for word in description_text.split():
        candidate = f"{current_line} {word}".strip()
        if current_line and description_font.measure(candidate) > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)

    y = event.height * 0.43
    line_height = description_font.metrics("linespace") + max(3, int(event.height * 0.008))
    for line in lines:
        canvas.create_text(
            event.width / 2,
            y,
            text=line,
            font=description_font,
            fill="#d0d0d0",
            justify="center",
            anchor="n",
            tags="description",
        )
        y += line_height

def draw_scanlines(event):
    canvas.delete("scanline")
    for y in range(1, event.height, 2):
        canvas.create_line(0, y, event.width, y, fill="#1a1a1a", tags="scanline")
    draw_logo(event)
    draw_description(event)
    canvas.tag_raise("scanline")

canvas.bind("<Configure>", draw_scanlines)

root.mainloop()