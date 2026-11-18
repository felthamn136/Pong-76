#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
APPDIR="$ROOT/target/appimage/Pong76.AppDir"
OUTPUT="$ROOT/dist/Pong-76-x86_64.AppImage"
APPIMAGETOOL="${APPIMAGETOOL:-appimagetool}"

if ! command -v "$APPIMAGETOOL" >/dev/null 2>&1; then
    printf 'appimagetool was not found; set APPIMAGETOOL to its executable path.\n' >&2
    exit 1
fi

cargo build --manifest-path "$ROOT/Cargo.toml" --release
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib" "$ROOT/dist"
cp "$ROOT/target/release/pong76" "$APPDIR/usr/bin/pong76"
cp "$SCRIPT_DIR/AppRun" "$APPDIR/AppRun"
cp "$SCRIPT_DIR/pong76.desktop" "$APPDIR/pong76.desktop"
cp "$ROOT/assets/pong76-logo.png" "$APPDIR/pong76.png"

for library in libudev.so.1 libasound.so.2 libgcc_s.so.1; do
    library_path="$(ldconfig -p | awk -v library="$library" '$1 == library && /x86-64/ { print $NF; exit }')"
    if [ -z "$library_path" ]; then
        printf 'Required runtime library was not found: %s\n' "$library" >&2
        exit 1
    fi
    cp -L "$library_path" "$APPDIR/usr/lib/$library"
done

chmod a+rx "$APPDIR/AppRun" "$APPDIR/usr/bin/pong76"
chmod a+r "$APPDIR/pong76.desktop" "$APPDIR/pong76.png" "$APPDIR/usr/lib/"*

ARCH=x86_64 "$APPIMAGETOOL" --no-appstream "$APPDIR" "$OUTPUT"
printf 'Created %s\n' "$OUTPUT"
