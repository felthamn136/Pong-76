# Projects Notes

<p align="center">
  <img src="assets/pong76-banner.png" alt="Pong '76 logo on a retro striped background" width="600">
</p>

Pong '76 is an experimental Copilot AI-developed game project inspired by the
classic *Squash* game found on late-1970s
Grandstand TV gaming consoles, including the Adman Grandstand 3000 and Video
Sports Centre 6000 Colour.

## Game setup screen

The application starts on the setup screen in a resizable 800 x 600 window.
The screen has a dark brown background matching the banner, the Pong '76 logo,
and two rows of compact, metal lever switches
inspired by 1970s hardware for player mode, paddle size, ball angle, game
speed, scanlines, keyboard or joystick controls, game colour, and autoserve.
The ball-angle slider offers 20 or 40 degrees; speed ranges from slow to fast.
Game colour choices are white, green, and amber. Scanlines are not shown on the
setup screen; the scanlines setting applies to gameplay.

Switch labels use the Righteous font by Astigmatic, licensed under the
[SIL Open Font License](assets/Righteous-OFL.txt).

## Gameplay

“Start Game” begins a Pong match in the same window. Small or
large selects paddle height; 20- or 40-degree settings affect serves and
returns; slow or fast changes ball speed. One-player mode pits the user against
the computer. Keyboard mode uses W/S for Player 1; the up/down arrows control
Player 2 in two-player mode. Joystick mode uses each controller's left stick
or D-pad vertically; the South button (A/X) serves and replays. Connect one
controller for one-player mode or two for two-player mode. Joystick support is
built into the game using Gilrs; select JOYSTICK in setup and run the game
normally.

The selected colour applies to gameplay, while enabled scanlines stay behind
the game. Paddles and the ball scale with the window. A match is won when a
player reaches at least 11 points with a two-point lead. Autoserve
defaults to “No”, which waits for Space or the controller's South button
(A/X); “Yes” launches automatically at the start and after points. Use the
Pause/Resume button to stop or continue a match. Press Escape to return to
setup or Enter after a win to start a new match.

Sound effects use synthesized tones: 480 Hz for 50 ms on paddle hits, 240 Hz
for 50 ms on wall bounces, and 240 Hz for 250 ms when a point is scored. If
audio output is unavailable, the game remains playable and reports the issue
in the UI and terminal.

The project was created through carefully engineered prompts designed by Neil
Feltham to explore modern AI-assisted game development.

The rounded arcade-style app icon uses the Pong '76 logo for the game window
and packaged shortcuts.

## Run

Install Rust and Cargo, then run the Rust implementation:

```bash
cargo run
```

Run the game-logic tests with `cargo test`.

## Linux AppImage

The x86_64 AppImage is available at
[dist/Pong-76-x86_64.AppImage](./dist/Pong-76-x86_64.AppImage). To rebuild it,
install `appimagetool` and run:

```bash
APPIMAGETOOL=/path/to/appimagetool packaging/linux/build-appimage.sh
```

## Linux Snap

The amd64 Snap package is available at
[dist/pong-76_0.1.0_amd64.snap](./dist/pong-76_0.1.0_amd64.snap). To rebuild
it, run:

```bash
packaging/snap/build-snap.sh
```

Install the local package with:

```bash
sudo snap install --dangerous dist/pong-76_0.1.0_amd64.snap
```

## Linux Flatpak

The x86_64 Flatpak bundle is available at
[dist/Pong-76.flatpak](./dist/Pong-76.flatpak). To rebuild it, install Cargo,
the Flatpak CLI, and the Freedesktop Platform 26.08 runtime, then run:

```bash
packaging/flatpak/build-flatpak.sh
```

Install the local bundle with:

```bash
flatpak install --user dist/Pong-76.flatpak
```

## Windows installer

The x86_64 Windows installer is available at
[dist/Pong-76-Setup.exe](./dist/Pong-76-Setup.exe). To rebuild it on Linux,
install Rust, the `x86_64-pc-windows-gnu` Rust target, MinGW-w64, and NSIS, then
run:

```bash
rustup target add x86_64-pc-windows-gnu
packaging/windows/build-windows.sh
```

The installer adds a Start Menu shortcut and an uninstaller.
