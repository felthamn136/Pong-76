# Tkinter provides the window and canvas; tkfont provides measurable, scalable text.
import tkinter as tk
import tkinter.font as tkfont

# Create the resizable 4:3 attraction window with a black background.
root = tk.Tk()
root.title("Pong '76")
root.geometry("800x600")
root.resizable(True, True)
root.configure(bg="black")
root.wm_aspect(4, 3, 4, 3)

# Create a canvas to draw the logo, description, and CRT scanline effect.
# At 480p, alternating active and dark rows approximate 240p (or 224-line) output.
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Define the title and bold font used for the attraction-screen logo.
logo_text = "PONG '76"
logo_font = tkfont.Font(root=root, family="Helvetica", size=72, weight="bold")

# Store the historical inspiration and project-development description shown below the logo.
description_text = (
    "This experimental Copilot AI-developed game is inspired by the classic Squash game "
    "found on late-1970s Grandstand TV gaming consoles, including the Adman Grandstand "
    "3000 and Video Sports Centre 6000 Colour. The project was created through a series "
    "of carefully engineered prompts designed by Neil Feltham to explore the "
    "capabilities of modern AI-assisted game development."
)
description_font = tkfont.Font(root=root, family="Helvetica", size=16)

# Create the game-entry button; its canvas position is updated below the description.
continue_button = tk.Button(
    root,
    text="Continue to Game",
    font=("Helvetica", 14, "bold"),
    bg="#f4e8c1",
    fg="black",
    activebackground="#fff1c7",
    relief="flat",
    padx=18,
    pady=8,
)
continue_button_window = canvas.create_window(0, 0, window=continue_button)

# Redraw each letter at a calculated position to make a centered, shallow-curved logo.
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

# Wrap the description to the current canvas width, add row spacing, and place the button below it.
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

    # Keep the button centered below the last description row as the window resizes.
    button_gap = max(16, int(event.height * 0.03))
    button_y = y + button_gap + continue_button.winfo_reqheight() / 2
    canvas.coords(continue_button_window, event.width / 2, button_y)

# Redraw scanlines and resize the logo, description, and button with the canvas.
def draw_scanlines(event):
    canvas.delete("scanline")
    for y in range(1, event.height, 2):
        canvas.create_line(0, y, event.width, y, fill="#1a1a1a", tags="scanline")
    draw_logo(event)
    draw_description(event)
    canvas.tag_raise("scanline")
    # Keep the button above the scanline overlay so it remains clear and clickable.
    canvas.tag_raise(continue_button_window)

# Re-render the attraction screen whenever the canvas dimensions change.
canvas.bind("<Configure>", draw_scanlines)

# Start Tkinter's event loop and display the window.
root.mainloop()