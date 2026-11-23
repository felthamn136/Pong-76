# Projects Notes

<p align="center">
  <img src="assets/pong76-banner.png" alt="Pong '76 logo on a retro striped background" width="600">
</p>

Pong '76 is an experimental Copilot AI-developed game project inspired by the
classic *Squash* game found on late-1970s
Grandstand TV gaming consoles, including the Adman Grandstand 3000 and Video
Sports Centre 6000 Colour.

## Game setup screen

The application starts on the setup screen in a resizable 960 x 540 window
(minimum 640 x 480).
The screen has a dark brown background matching the banner, a scaled-down copy
of the Pong '76 banner, and two spaced rows of individually framed, bronze-toned
metal lever switches inspired by 1970s hardware. The switches configure player
mode, paddle size, ball angle, game speed, scanlines, keyboard or joystick
controls, game colour, and autoserve.
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

Moving a paddle as the ball hits it adds slice, and off-center hits add spin.
The spin curves the ball vertically while keeping it traveling away from the
paddle that hit it.

The selected colour applies to gameplay, while enabled scanlines stay behind
the game. The gameplay area scales to fit the window while retaining a 16:9
aspect ratio, with black bars when needed. Paddles and the ball scale with the
gameplay area. A match is won when a
player reaches at least 11 points with a two-point lead. Autoserve
defaults to “No”, which waits for Space or the controller's South button
(A/X); “Yes” launches automatically at the start and after points. Use the
Pause/Resume button to stop or continue a match. Press Escape to return to
setup or Enter after a win to start a new match.

Sound effects use synthesized tones: 480 Hz for 50 ms on paddle hits, 240 Hz
for 50 ms on wall bounces, and 240 Hz for 250 ms when a point is scored. If
audio output is unavailable, the game remains playable and reports the issue
in the UI and terminal.

## ZX81 version

A numbered Sinclair BASIC listing is available at [ports/zx81/pong76.bas](ports/zx81/pong76.bas).
The compiled, auto-starting ZX81 image is [ports/zx81/pong76.p](ports/zx81/pong76.p).
It is intended for a ZX81 with a 16K RAM expansion. Enter `1` or `2` and press
Enter to choose one player against the computer or two players. Player 1 uses
A/Z and Player 2 uses O/L. The paddles, ball, and walls use ZX81 block graphics.
The program reads the keyboard matrix directly so both paddles can be moved
independently. First to 11 points with a two-point lead wins; type `RUN` to play
again. The game updates only the changed screen cells for faster gameplay
while keeping the display visible.

The `.p` image starts automatically when loaded. Alternatively, enter the
listing and type `RUN`; save it to tape with `SAVE "PONG76"`. Line 1 reserves
space for the keyboard-reading machine code initialized by lines 2–11: keep
the nine characters after `REM` intact when entering the listing.

To rebuild the image from the listing, use
[zmakebas with ZX81 support](https://github.com/ryangray/zmakebas):

```bash
zmakebas -p -a 2 -o ports/zx81/pong76.p ports/zx81/pong76.bas
```

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

If the project is on a network drive and Cargo reports an incremental
compilation cache error, use a local target directory instead:

```bash
CARGO_TARGET_DIR="$HOME/.cache/pong76-target" cargo run
```

Use the same `CARGO_TARGET_DIR` with `cargo test`. The Linux packaging scripts
expect the default `target` directory and should be run without this setting.

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

## Windows installer and portable version

The x86_64 [WiX installer](./dist/Pong-76-Setup.msi) includes a feature
selection screen where the optional desktop shortcut can be enabled. It
installs a Start Menu shortcut and can be removed through Windows settings.
The [portable ZIP](./dist/Pong-76-Portable.zip) can be extracted and run
without installation.

To rebuild on Linux, install Rust, the `x86_64-pc-windows-gnu` Rust target,
MinGW-w64, `zip`, Wine, a Windows .NET runtime, and WiX 6 with
`WixToolset.UI.wixext`. WiX only supports Windows, so run it through Wine:

```bash
rustup target add x86_64-pc-windows-gnu
wix extension add -g WixToolset.UI.wixext/6.0.2
WIX_WINE_DOTNET=/path/to/windows-dotnet/dotnet.exe \
WIX_WINE_DLL=/path/to/wix/6.0.2/tools/net6.0/any/wix.dll \
WIX_UI_EXTENSION=/path/to/WixToolset.UI.wixext.dll \
packaging/windows/build-windows.sh
```
