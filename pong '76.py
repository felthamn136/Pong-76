# Tkinter provides the window and canvas; tkfont provides measurable, scalable text.
import tkinter as tk
import tkinter.font as tkfont
import math
import random
import time
from tkinter import messagebox

# Create the resizable 4:3 attraction window with a black background.
root = tk.Tk()
root.title("Pong '76")
root.geometry("800x600")
root.resizable(True, True)
root.configure(bg="black")
root.wm_aspect(4, 3, 4, 3)

# Create a full-window canvas for the logo, description, game, and CRT scanlines.
# At 480p, alternating active and dark rows approximate 240p (or 224-line) output.
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)
current_screen = "attraction"
# Keep match data, rendered item IDs, timer state, keys, and optional joystick handles.
game_state = {}
game_items = {}
game_after_id = None
pressed_keys = set()
joystick_module = None
joysticks = []

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

start_button = tk.Button(
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
start_button.pack(pady=(16, 0))
setup_panel_window = canvas.create_window(0, 0, window=setup_panel)
canvas.itemconfigure(setup_panel_window, state="hidden")

def draw_setting_slider(key):
    """Draw a setting slider and highlight the selected choice."""
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

def set_setting(key, event):
    """Choose the closest slider option and immediately apply display changes."""
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

def draw_logo(width, height, size_scale=0.09, baseline_scale=0.21):
    """Position the logo's letters along a centered, shallow curve."""
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

def draw_description(width, height):
    """Wrap and space the description, then position its button below it."""
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

# Gameplay is drawn on the shared canvas and reads the selected setup variables.
def _game_layout(width, height):
    """Calculate court, paddle, and ball dimensions for the current canvas size."""
    # Keep court objects proportional so the game remains playable at any 4:3 size.
    paddle_height = height * (0.12 if paddle_size.get() == "small" else 0.2)
    paddle_width = max(8, width * 0.0125)
    paddle_margin = width * 0.07
    return {
        "top": height * 0.14,
        "bottom": height * 0.92,
        "left_x": paddle_margin,
        "right_x": width - paddle_margin - paddle_width,
        "paddle_width": paddle_width,
        "paddle_height": paddle_height,
        "ball_radius": max(5, width * 0.012),
        "paddle_speed": 420 * height / 600,
    }

def _phosphor_shades(color):
    """Create darker phosphor colors for the layered object glow."""
    channels = [int(color[index : index + 2], 16) for index in (1, 3, 5)]
    return [
        "#{:02x}{:02x}{:02x}".format(
            *(round(channel * brightness) for channel in channels)
        )
        for brightness in (0.16, 0.3, 0.52)
    ]

def _create_glow_layers(shades):
    """Create transparent outlines that simulate a CRT phosphor halo."""
    return [
        canvas.create_rectangle(
            0,
            0,
            0,
            0,
            fill="",
            outline=shade,
            width=width,
            tags="game",
        )
        for shade, width in zip(shades, (8, 5, 2))
    ]

def _position_glow_layers(layers, coordinates):
    """Move every phosphor outline with its matching game object."""
    for layer in layers:
        canvas.coords(layer, *coordinates)

def _draw_game_screen(width, height):
    """Draw the Pong court and update all game-object positions."""
    global game_items
    width = max(1, width)
    height = max(1, height)
    # Scale the active match coordinates when the window is resized.
    old_width = game_state.get("width", width)
    old_height = game_state.get("height", height)
    if old_width != width or old_height != height:
        game_state["ball_x"] *= width / old_width
        game_state["ball_y"] *= height / old_height
        game_state["left_y"] *= height / old_height
        game_state["right_y"] *= height / old_height
        game_state["ball_vx"] *= width / old_width
        game_state["ball_vy"] *= height / old_height
        game_state["width"] = width
        game_state["height"] = height

    layout = _game_layout(width, height)
    color = game_colours[game_colour.get()]
    glow_shades = _phosphor_shades(color)
    center_x = width / 2
    # Create canvas objects once; each frame only updates their coordinates and text.
    if not game_items:
        game_items = {
            "center_line": canvas.create_line(
                center_x,
                layout["top"],
                center_x,
                layout["bottom"],
                fill="#565656",
                width=4,
                dash=(8, 10),
                tags="game",
            ),
            "left_glow": _create_glow_layers(glow_shades),
            "left_paddle": canvas.create_rectangle(0, 0, 0, 0, fill=color, outline="", tags="game"),
            "right_glow": _create_glow_layers(glow_shades),
            "right_paddle": canvas.create_rectangle(0, 0, 0, 0, fill=color, outline="", tags="game"),
            "ball_glow": _create_glow_layers(glow_shades),
            "ball": canvas.create_rectangle(0, 0, 0, 0, fill=color, outline="", tags="game"),
            "left_score": canvas.create_text(
                width * 0.25, height * 0.07, fill=color, font=("Helvetica", 26, "bold"), tags="game"
            ),
            "right_score": canvas.create_text(
                width * 0.75, height * 0.07, fill=color, font=("Helvetica", 26, "bold"), tags="game"
            ),
            "hint": canvas.create_text(
                center_x,
                height * 0.985,
                fill="#a0a0a0",
                font=("Helvetica", max(8, int(width * 0.014))),
                width=width * 0.94,
                anchor="s",
                justify="center",
                tags="game",
            ),
            "game_over": canvas.create_text(
                center_x,
                height / 2,
                fill=color,
                font=("Helvetica", max(22, int(width * 0.04)), "bold"),
                justify="center",
                tags="game",
            ),
        }

    radius = layout["ball_radius"]
    half_paddle = layout["paddle_height"] / 2
    left_coords = (
        layout["left_x"],
        game_state["left_y"] - half_paddle,
        layout["left_x"] + layout["paddle_width"],
        game_state["left_y"] + half_paddle,
    )
    right_coords = (
        layout["right_x"],
        game_state["right_y"] - half_paddle,
        layout["right_x"] + layout["paddle_width"],
        game_state["right_y"] + half_paddle,
    )
    ball_coords = (
        game_state["ball_x"] - radius,
        game_state["ball_y"] - radius,
        game_state["ball_x"] + radius,
        game_state["ball_y"] + radius,
    )
    canvas.coords(
        game_items["center_line"], center_x, layout["top"], center_x, layout["bottom"]
    )
    _position_glow_layers(game_items["left_glow"], left_coords)
    canvas.coords(game_items["left_paddle"], *left_coords)
    _position_glow_layers(game_items["right_glow"], right_coords)
    canvas.coords(game_items["right_paddle"], *right_coords)
    _position_glow_layers(game_items["ball_glow"], ball_coords)
    canvas.coords(game_items["ball"], *ball_coords)
    canvas.coords(game_items["left_score"], width * 0.25, height * 0.07)
    canvas.coords(game_items["right_score"], width * 0.75, height * 0.07)
    left_label = "PLAYER 1" if player_count.get() == 2 else "YOU"
    right_label = "PLAYER 2" if player_count.get() == 2 else "CPU"
    canvas.itemconfigure(
        game_items["left_score"],
        text=f"{left_label}  {game_state['left_score']}",
        fill=color,
    )
    canvas.itemconfigure(
        game_items["right_score"],
        text=f"{right_label}  {game_state['right_score']}",
        fill=color,
    )
    if control_type.get() == "joystick":
        controls_hint = "JOYSTICK  |  ESC: SETUP"
    elif player_count.get() == 2:
        controls_hint = "P1: W/S  |  P2: UP/DOWN  |  ESC: SETUP"
    else:
        controls_hint = "W/S: MOVE  |  ESC: SETUP"
    canvas.coords(game_items["hint"], center_x, height * 0.985)
    canvas.itemconfigure(game_items["hint"], text=controls_hint)

    if game_state["game_over"]:
        canvas.coords(game_items["game_over"], center_x, height / 2)
        canvas.itemconfigure(
            game_items["game_over"],
            text=f"{game_state['winner']} WINS\nPRESS ENTER TO PLAY AGAIN",
            state="normal",
            fill=color,
        )
    else:
        canvas.itemconfigure(game_items["game_over"], state="hidden")

def _reset_ball(direction=None):
    """Serve the ball at the selected angle and current speed."""
    if direction is None:
        direction = random.choice((-1, 1))
    angle = math.radians(ball_angle.get())
    speed = game_state["ball_speed"]
    game_state["ball_x"] = game_state["width"] / 2
    game_state["ball_y"] = game_state["height"] / 2
    game_state["ball_vx"] = direction * speed * math.cos(angle)
    game_state["ball_vy"] = random.choice((-1, 1)) * speed * math.sin(angle)
    game_state["serve_until"] = time.monotonic() + 0.65

def _prepare_joysticks():
    """Initialize enough joysticks for the selected player count."""
    global joystick_module
    # Keep keyboard play dependency-free; load Pygame only when joystick input is selected.
    try:
        import pygame as pygame_runtime
    except ImportError:
        messagebox.showerror(
            "Joystick support unavailable",
            "Install joystick support with: python -m pip install -r requirements-joystick.txt",
        )
        return False

    joystick_module = pygame_runtime
    try:
        # A hidden SDL display lets Pygame poll devices without replacing the Tk window.
        joystick_module.display.init()
        joystick_module.display.set_mode((1, 1), joystick_module.HIDDEN)
        joystick_module.joystick.init()
        required = player_count.get()
        available = joystick_module.joystick.get_count()
        if available < required:
            _close_joysticks()
            messagebox.showerror(
                "Joystick not found",
                f"Connect {required} joystick{'s' if required != 1 else ''} before starting.",
            )
            return False
        for index in range(required):
            joystick = joystick_module.joystick.Joystick(index)
            joystick.init()
            joysticks.append(joystick)
    except joystick_module.error as error:
        _close_joysticks()
        messagebox.showerror("Joystick error", str(error))
        return False
    return True

def _close_joysticks():
    """Release initialized joystick devices when leaving the game."""
    global joystick_module
    for joystick in joysticks:
        joystick.quit()
    joysticks.clear()
    if joystick_module is not None:
        joystick_module.joystick.quit()
        joystick_module.display.quit()
        joystick_module = None

def start_game():
    """Start a new match using the selected control and gameplay settings."""
    global current_screen
    if control_type.get() == "joystick" and not _prepare_joysticks():
        return

    # Capture the setup choices when the match starts and reset all match state.
    width = max(1, canvas.winfo_width())
    height = max(1, canvas.winfo_height())
    game_state.clear()
    game_state.update(
        {
            "width": width,
            "height": height,
            "left_y": height / 2,
            "right_y": height / 2,
            "left_score": 0,
            "right_score": 0,
            "ball_speed": (330 if game_speed.get() == "slow" else 500) * width / 800,
            "game_over": False,
            "winner": "",
            "last_tick": time.monotonic(),
        }
    )
    game_items.clear()
    canvas.delete("game")
    pressed_keys.clear()
    current_screen = "game"
    _reset_ball()
    render_screen(width, height)
    root.focus_set()
    _game_loop()

def _finish_game():
    """Stop the game loop and return to setup when Escape is pressed."""
    global current_screen, game_after_id
    if game_after_id is not None:
        root.after_cancel(game_after_id)
        game_after_id = None
    _close_joysticks()
    pressed_keys.clear()
    game_state.clear()
    game_items.clear()
    canvas.delete("game")
    current_screen = "setup"
    render_screen(canvas.winfo_width(), canvas.winfo_height())

def _reset_match():
    """Reset both scores and serve a fresh match."""
    game_state["left_score"] = 0
    game_state["right_score"] = 0
    game_state["game_over"] = False
    game_state["winner"] = ""
    _reset_ball()
    _draw_game_screen(canvas.winfo_width(), canvas.winfo_height())

def _on_key_press(event):
    """Track game controls and handle the game-over and exit keys."""
    if current_screen != "game":
        return
    key = event.keysym.lower()
    if key == "escape":
        _finish_game()
        return "break"
    if game_state["game_over"] and key in {"return", "kp_enter"}:
        _reset_match()
        return "break"
    if control_type.get() == "keyboard":
        pressed_keys.add(key)

def _on_key_release(event):
    """Remove a released key from the active movement set."""
    pressed_keys.discard(event.keysym.lower())

def _move_paddle(position, direction, speed, elapsed, top, bottom, half_height):
    """Move a paddle while keeping it inside the court."""
    position += direction * speed * elapsed
    return max(top + half_height, min(bottom - half_height, position))

def _bounce_from_paddle(direction, paddle_y, half_height):
    """Reflect the ball and vary its return angle by the paddle impact point."""
    offset = max(-1, min(1, (game_state["ball_y"] - paddle_y) / half_height))
    angle = math.radians(ball_angle.get() + abs(offset) * 24)
    speed = math.hypot(game_state["ball_vx"], game_state["ball_vy"])
    game_state["ball_vx"] = direction * speed * math.cos(angle)
    game_state["ball_vy"] = (1 if offset >= 0 else -1) * speed * math.sin(angle)

def _game_loop():
    """Advance paddle and ball physics at a steady Tkinter timer interval."""
    global game_after_id
    game_after_id = None
    if current_screen != "game":
        return

    now = time.monotonic()
    elapsed = min(now - game_state["last_tick"], 0.05)
    game_state["last_tick"] = now
    layout = _game_layout(game_state["width"], game_state["height"])
    paddle_half = layout["paddle_height"] / 2
    left_direction = 0
    right_direction = 0

    # Read either key state or controller axes, based on the setup selection.
    if control_type.get() == "keyboard":
        left_direction = int("s" in pressed_keys) - int("w" in pressed_keys)
        if player_count.get() == 2:
            right_direction = int("down" in pressed_keys) - int("up" in pressed_keys)
    else:
        try:
            joystick_module.event.pump()
            left_axis = joysticks[0].get_axis(1) if joysticks[0].get_numaxes() > 1 else 0
            left_direction = left_axis if abs(left_axis) > 0.18 else 0
            if player_count.get() == 2:
                right_axis = (
                    joysticks[1].get_axis(1)
                    if joysticks[1].get_numaxes() > 1
                    else 0
                )
                right_direction = right_axis if abs(right_axis) > 0.18 else 0
        except joystick_module.error as error:
            _finish_game()
            messagebox.showerror("Joystick error", str(error))
            return

    paddle_speed = layout["paddle_speed"]
    game_state["left_y"] = _move_paddle(
        game_state["left_y"],
        left_direction,
        paddle_speed,
        elapsed,
        layout["top"],
        layout["bottom"],
        paddle_half,
    )
    if player_count.get() == 2:
        game_state["right_y"] = _move_paddle(
            game_state["right_y"],
            right_direction,
            paddle_speed,
            elapsed,
            layout["top"],
            layout["bottom"],
            paddle_half,
        )
    else:
        # In solo play, the computer tracks the ball but moves more slowly than a player.
        target_y = (
            game_state["ball_y"]
            if game_state["ball_vx"] > 0
            else game_state["height"] / 2
        )
        difference = target_y - game_state["right_y"]
        ai_direction = 1 if difference > 0 else -1
        ai_step = min(abs(difference), paddle_speed * 0.78 * elapsed)
        game_state["right_y"] += ai_direction * ai_step

    # Advance the ball, reflect it from the court and paddles, then award points.
    if not game_state["game_over"] and now >= game_state["serve_until"]:
        game_state["ball_x"] += game_state["ball_vx"] * elapsed
        game_state["ball_y"] += game_state["ball_vy"] * elapsed
        radius = layout["ball_radius"]
        if game_state["ball_y"] - radius < layout["top"]:
            game_state["ball_y"] = layout["top"] + radius
            game_state["ball_vy"] = abs(game_state["ball_vy"])
        elif game_state["ball_y"] + radius > layout["bottom"]:
            game_state["ball_y"] = layout["bottom"] - radius
            game_state["ball_vy"] = -abs(game_state["ball_vy"])

        left_face = layout["left_x"] + layout["paddle_width"]
        right_face = layout["right_x"]
        if (
            game_state["ball_vx"] < 0
            and game_state["ball_x"] - radius <= left_face
            and game_state["ball_x"] + radius >= layout["left_x"]
            and abs(game_state["ball_y"] - game_state["left_y"])
            <= paddle_half + radius
        ):
            game_state["ball_x"] = left_face + radius
            _bounce_from_paddle(1, game_state["left_y"], paddle_half)
        elif (
            game_state["ball_vx"] > 0
            and game_state["ball_x"] + radius >= right_face
            and game_state["ball_x"] - radius
            <= layout["right_x"] + layout["paddle_width"]
            and abs(game_state["ball_y"] - game_state["right_y"])
            <= paddle_half + radius
        ):
            game_state["ball_x"] = right_face - radius
            _bounce_from_paddle(-1, game_state["right_y"], paddle_half)

        if game_state["ball_x"] + radius < 0:
            game_state["right_score"] += 1
            _reset_ball(-1)
        elif game_state["ball_x"] - radius > game_state["width"]:
            game_state["left_score"] += 1
            _reset_ball(1)

        # End the match at 11 points, requiring a two-point winning margin.
        if max(game_state["left_score"], game_state["right_score"]) >= 11:
            if abs(game_state["left_score"] - game_state["right_score"]) >= 2:
                game_state["game_over"] = True
                if player_count.get() == 2:
                    game_state["winner"] = (
                        "PLAYER 1"
                        if game_state["left_score"] > game_state["right_score"]
                        else "PLAYER 2"
                    )
                else:
                    game_state["winner"] = (
                        "YOU" if game_state["left_score"] > game_state["right_score"] else "CPU"
                    )

    _draw_game_screen(canvas.winfo_width(), canvas.winfo_height())
    game_after_id = root.after(16, _game_loop)

def render_screen(width, height):
    """Render the attraction, setup, or gameplay view for the current canvas size."""
    canvas.delete("scanline")
    # Render scanlines beneath the active view, then raise them as a CRT overlay.
    if scanlines_enabled.get():
        for y in range(1, height, 2):
            canvas.create_line(0, y, width, y, fill="#1a1a1a", tags="scanline")

    if current_screen == "attraction":
        canvas.itemconfigure(continue_button_window, state="normal")
        canvas.itemconfigure(setup_panel_window, state="hidden")
        draw_logo(width, height)
        draw_description(width, height)
        canvas.tag_raise(continue_button_window)
    elif current_screen == "setup":
        canvas.itemconfigure(continue_button_window, state="hidden")
        canvas.itemconfigure(setup_panel_window, state="normal")
        draw_logo(width, height, size_scale=0.07, baseline_scale=0.13)
        canvas.delete("description")
        canvas.coords(setup_panel_window, width / 2, height * 0.58)
        for key in game_settings:
            draw_setting_slider(key)
    else:
        canvas.itemconfigure(continue_button_window, state="hidden")
        canvas.itemconfigure(setup_panel_window, state="hidden")
        canvas.delete("logo")
        canvas.delete("description")
        _draw_game_screen(width, height)

    canvas.tag_raise("scanline")
    if current_screen == "attraction":
        canvas.tag_raise(continue_button_window)
    elif current_screen == "setup":
        canvas.tag_raise(setup_panel_window)

def show_game_setup():
    """Show the setup screen after the attraction screen's continue button."""
    global current_screen
    current_screen = "setup"
    render_screen(canvas.winfo_width(), canvas.winfo_height())

continue_button.configure(command=show_game_setup)
start_button.configure(command=start_game)

# Route canvas resizes and keyboard events to the active screen and game controls.
canvas.bind(
    "<Configure>",
    lambda event: render_screen(event.width, event.height),
)
root.bind_all("<KeyPress>", _on_key_press)
root.bind_all("<KeyRelease>", _on_key_release)

# Start Tkinter's event loop and display the window.
root.mainloop()