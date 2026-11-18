# Tkinter provides the window and canvas; tkfont provides measurable, scalable text.
import tkinter as tk
import tkinter.font as tkfont

# Create the resizable 4:3 attraction window with a black background.
root = tk.Tk()
root.title("Pong '76")
root.geometry("800x600")
root.resizable(True, True)
root.configure(bg="#211a12")
root.wm_aspect(4, 3, 4, 3)

# Inset the black display to leave a narrow, dark console-colored border around it.
# Create a canvas to draw the logo, description, and CRT scanline effect.
# At 480p, alternating active and dark rows approximate 240p (or 224-line) output.
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True, padx=10, pady=10)
current_screen = "attraction"

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

# Game Setup Screen
# Store the eight game and display settings controlled by the setup sliders.
player_count = tk.IntVar(root, value=1)
paddle_size = tk.StringVar(root, value="small")
ball_angle = tk.IntVar(root, value=20)
game_speed = tk.StringVar(root, value="slow")
scanlines_enabled = tk.BooleanVar(root, value=True)
control_type = tk.StringVar(root, value="keyboard")
game_colour = tk.StringVar(root, value="white")
fullscreen_enabled = tk.BooleanVar(root, value=False)
game_colours = {
    "white": "#f4f4f4",
    "green": "#7dff7a",
    "amber": "#f4e8c1",
}
game_settings = {
    # First row: player mode and gameplay tuning.
    "players": {
        "title": "PLAYER MODE",
        "variable": player_count,
        "choices": [("PLAYER 1", 1), ("PLAYER 2", 2)],
    },
    "paddle_size": {
        "title": "PADDLE SIZE",
        "variable": paddle_size,
        "choices": [("SMALL", "small"), ("LARGE", "large")],
    },
    "ball_angle": {
        "title": "BALL ANGLE",
        "variable": ball_angle,
        "choices": [("20 DEGREES", 20), ("40 DEGREES", 40)],
    },
    "game_speed": {
        "title": "GAME SPEED",
        "variable": game_speed,
        "choices": [("SLOW", "slow"), ("FAST", "fast")],
    },
    # Second row: CRT display, input method, display colour, and window mode.
    "scanlines": {
        "title": "SCANLINES",
        "variable": scanlines_enabled,
        "choices": [("ON", True), ("OFF", False)],
    },
    "controls": {
        "title": "CONTROLS",
        "variable": control_type,
        "choices": [("KEYBOARD", "keyboard"), ("JOYSTICK", "joystick")],
    },
    "game_colour": {
        "title": "GAME COLOUR",
        "variable": game_colour,
        "choices": [
            ("WHITE", "white"),
            ("GREEN", "green"),
            ("AMBER", "amber"),
        ],
    },
    "fullscreen": {
        "title": "FULLSCREEN",
        "variable": fullscreen_enabled,
        "choices": [("ON", True), ("OFF", False)],
    },
}
setup_panel = tk.Frame(root, bg="black")
tk.Label(
    setup_panel,
    text="GAME SETUP",
    font=("Helvetica", 22, "bold"),
    fg="#f4e8c1",
    bg="black",
).pack(pady=(0, 12))
# Arrange the eight matching vertical console-style sliders in two rows.
settings_grid = tk.Frame(setup_panel, bg="black")
settings_grid.pack()
setting_canvases = {}
for index, (key, setting) in enumerate(game_settings.items()):
    setting_frame = tk.Frame(settings_grid, bg="black")
    setting_frame.grid(row=index // 4, column=index % 4, padx=5, pady=4)
    tk.Label(
        setting_frame,
        text=setting["title"],
        font=("Helvetica", 10, "bold"),
        fg="#d0d0d0",
        bg="black",
    ).pack(pady=(0, 6))
    slider_canvas = tk.Canvas(
        setting_frame,
        width=140,
        height=136,
        bg="black",
        highlightthickness=0,
        cursor="hand2",
        takefocus=True,
    )
    slider_canvas.pack()
    slider_canvas.bind(
        "<Button-1>", lambda event, slider_key=key: set_setting(slider_key, event)
    )
    slider_canvas.bind(
        "<B1-Motion>", lambda event, slider_key=key: set_setting(slider_key, event)
    )
    setting_canvases[key] = slider_canvas

back_button = tk.Button(
    setup_panel,
    text="Start Game",
    font=("Helvetica", 12, "bold"),
    bg="#242424",
    fg="#f4e8c1",
    activebackground="#383838",
    relief="flat",
    padx=14,
    pady=7,
)
back_button.pack(pady=(20, 0))
setup_panel_window = canvas.create_window(0, 0, window=setup_panel)
canvas.itemconfigure(setup_panel_window, state="hidden")

# Draw a shared 1970s console-style slider and emphasize the selected choice.
def draw_setting_slider(key):
    slider = setting_canvases[key]
    setting = game_settings[key]
    value = setting["variable"].get()
    choices = setting["choices"]
    slider_top = 44
    slider_bottom = 92
    slider.delete("all")
    slider.create_rectangle(
        2, 2, 138, 134, fill="#211a12", outline="#a27a45", width=2
    )
    slider.create_line(
        70, slider_top, 70, slider_bottom, fill="#70532f", width=18, capstyle=tk.ROUND
    )
    slider.create_line(
        70, slider_top, 70, slider_bottom, fill="#c49a5e", width=2, capstyle=tk.ROUND
    )

    positions = (
        [slider_top]
        if len(choices) == 1
        else [
            round(slider_top + index * (slider_bottom - slider_top) / (len(choices) - 1))
            for index in range(len(choices))
        ]
    )
    selected_index = next(
        index for index, (_, choice_value) in enumerate(choices) if choice_value == value
    )
    for index, (label, choice_value) in enumerate(choices):
        label_y = 18 if index == 0 else 118 if index == len(choices) - 1 else positions[index]
        label_x = 70 if index in (0, len(choices) - 1) else 96
        slider.create_text(
            label_x,
            label_y,
            text=label,
            fill="#ffe1a3" if choice_value == value else "#9c8760",
            font=("Helvetica", 9, "bold"),
            anchor="center" if label_x == 70 else "w",
        )

    knob_y = positions[selected_index]
    slider.create_rectangle(
        54, knob_y - 10, 86, knob_y + 10,
        fill="#c69a55", outline="#ffe0a0", width=2
    )
    slider.create_line(
        65, knob_y - 6, 65, knob_y + 6, fill="#ffe8b5", width=2
    )
    slider.create_line(
        75, knob_y - 6, 75, knob_y + 6, fill="#684b29", width=2
    )

# Select the nearest slider choice and apply display options immediately.
def set_setting(key, event):
    setting = game_settings[key]
    choices = setting["choices"]
    slider_top = 44
    slider_bottom = 92
    positions = (
        [slider_top]
        if len(choices) == 1
        else [
            round(slider_top + index * (slider_bottom - slider_top) / (len(choices) - 1))
            for index in range(len(choices))
        ]
    )
    selected_index = min(
        range(len(positions)), key=lambda index: abs(event.y - positions[index])
    )
    selected_value = choices[selected_index][1]
    setting["variable"].set(selected_value)

    if key == "fullscreen":
        root.attributes("-fullscreen", selected_value)
    if key in {"scanlines", "game_colour", "fullscreen"}:
        render_screen(canvas.winfo_width(), canvas.winfo_height())
    else:
        draw_setting_slider(key)

# Redraw each letter at a calculated position to make a centered, shallow-curved logo.
def draw_logo(width, height, size_scale=0.09, baseline_scale=0.21):
    canvas.delete("logo")
    logo_font.configure(size=max(24, int(width * size_scale)))
    widths = [logo_font.measure(character) for character in logo_text]
    text_width = sum(widths)
    x = (width - text_width) / 2
    half_width = text_width / 2
    baseline = height * baseline_scale
    arc_height = min(16, height * 0.025)

    for character, character_width in zip(logo_text, widths):
        center_x = x + character_width / 2
        curve_position = (center_x - width / 2) / half_width
        y = baseline + arc_height * curve_position**2
        canvas.create_text(
            center_x,
            y,
            text=character,
            font=logo_font,
            fill=game_colours[game_colour.get()],
            tags="logo",
        )
        x += character_width

# Wrap the description to the current canvas width, add row spacing, and place the button below it.
def draw_description(width, height):
    canvas.delete("description")
    description_font.configure(size=max(12, int(width * 0.02)))
    max_width = width * 0.78
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

    y = height * 0.43
    line_height = description_font.metrics("linespace") + max(3, int(height * 0.008))
    for line in lines:
        canvas.create_text(
            width / 2,
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
    button_gap = max(16, int(height * 0.03))
    button_y = y + button_gap + continue_button.winfo_reqheight() / 2
    canvas.coords(continue_button_window, width / 2, button_y)

# Draw the selected screen and keep its controls aligned with the canvas size.
def render_screen(width, height):
    canvas.delete("scanline")
    if scanlines_enabled.get():
        for y in range(1, height, 2):
            canvas.create_line(0, y, width, y, fill="#1a1a1a", tags="scanline")

    if current_screen == "attraction":
        canvas.itemconfigure(continue_button_window, state="normal")
        canvas.itemconfigure(setup_panel_window, state="hidden")
        draw_logo(width, height)
        draw_description(width, height)
        canvas.tag_raise(continue_button_window)
    else:
        canvas.itemconfigure(continue_button_window, state="hidden")
        canvas.itemconfigure(setup_panel_window, state="normal")
        draw_logo(width, height, size_scale=0.07, baseline_scale=0.13)
        canvas.delete("description")
        canvas.coords(setup_panel_window, width / 2, height * 0.58)
        for key in game_settings:
            draw_setting_slider(key)

    canvas.tag_raise("scanline")
    if current_screen == "attraction":
        canvas.tag_raise(continue_button_window)
    else:
        canvas.tag_raise(setup_panel_window)

# Switch screens when the attraction or setup navigation buttons are clicked.
def show_game_setup():
    global current_screen
    current_screen = "setup"
    render_screen(canvas.winfo_width(), canvas.winfo_height())

def show_attraction_screen():
    global current_screen
    current_screen = "attraction"
    render_screen(canvas.winfo_width(), canvas.winfo_height())

continue_button.configure(command=show_game_setup)
back_button.configure(command=show_attraction_screen)

# Re-render the active screen whenever the canvas is resized.
canvas.bind(
    "<Configure>",
    lambda event: render_screen(event.width, event.height),
)

# Start Tkinter's event loop and display the window.
root.mainloop()