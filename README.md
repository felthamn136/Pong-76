# Pong '76

Pong '76 is an experimental Copilot AI-developed game project. Its current
attraction screen is inspired by the classic *Squash* game found on late-1970s
Grandstand TV gaming consoles, including the Adman Grandstand 3000 and Video
Sports Centre 6000 Colour.

## Attraction screen

The Tkinter window currently provides:

- An 800×600 starting size with a resizable, 4:3 aspect ratio.
- An inset black background with a narrow console-colored border and
  near-black horizontal scanlines, redrawn as the window changes size.
- A bold, smoothly rendered “PONG '76” logo that follows a shallow curve and
  scales with the window, positioned slightly higher on the screen.
- Centered introductory text below the logo, with responsive wrapping and
  additional spacing between rows.
- A “Continue to Game” button that opens the game setup screen.

## Game setup screen

The setup screen uses a smaller version of the logo and two rows of compact,
vertical 1970s-console-style sliders for player mode, paddle size, ball angle,
game speed, scanlines, keyboard or joystick controls, game colour, and
fullscreen. The ball-angle slider ranges from 20 to 40 degrees; the speed
slider ranges from slow to fast. Game colour choices are white, green, and
amber. Scanline and fullscreen settings apply immediately, and the selected
colour is used for the logo. Other choices are stored for future gameplay.
A “Back to Attraction” button returns to the introduction. Gameplay is not
implemented yet.

The project was created through carefully engineered prompts designed by Neil
Feltham to explore modern AI-assisted game development.

## Run

Run the attraction screen with Python 3 and Tkinter installed:

```bash
python "pong '76.py"
```
