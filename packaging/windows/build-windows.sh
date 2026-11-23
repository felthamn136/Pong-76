#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
TARGET="x86_64-pc-windows-gnu"
WIX="${WIX:-wix}"

if ! command -v x86_64-w64-mingw32-gcc >/dev/null 2>&1 &&
    [ -z "${CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER:-}" ]; then
    printf 'The x86_64 MinGW-w64 compiler is required to build the Windows executable.\n' >&2
    exit 1
fi

if [ -n "${WIX_WINE_DOTNET:-}" ]; then
    if ! command -v wine >/dev/null 2>&1 || ! command -v winepath >/dev/null 2>&1; then
        printf 'Wine and winepath are required to run the Windows WiX tool.\n' >&2
        exit 1
    fi
    if [ ! -f "$WIX_WINE_DOTNET" ] || [ ! -f "${WIX_WINE_DLL:-}" ] ||
        [ ! -f "${WIX_UI_EXTENSION:-}" ]; then
        printf 'Set WIX_WINE_DOTNET, WIX_WINE_DLL, and WIX_UI_EXTENSION to existing files.\n' >&2
        exit 1
    fi
elif ! command -v "$WIX" >/dev/null 2>&1; then
    printf 'WiX was not found; install WiX and its UI extension, or set WIX to its executable path.\n' >&2
    exit 1
fi

if ! command -v zip >/dev/null 2>&1; then
    printf 'The zip command is required to build the portable package.\n' >&2
    exit 1
fi

if ! rustup target list --installed | grep -Fxq "$TARGET"; then
    printf 'Rust target %s is not installed; run: rustup target add %s\n' "$TARGET" "$TARGET" >&2
    exit 1
fi

TARGET_DIR="${CARGO_TARGET_DIR:-$ROOT/target}"
case "$TARGET_DIR" in
    /*) ;;
    *) TARGET_DIR="$PWD/$TARGET_DIR" ;;
esac
EXE="$TARGET_DIR/$TARGET/release/pong76.exe"

cargo build --manifest-path "$ROOT/Cargo.toml" --release --target "$TARGET"
mkdir -p "$ROOT/dist"
STAGING="$(mktemp -d "${TMPDIR:-/tmp}/pong76-portable.XXXXXX")"
trap 'rm -rf "$STAGING"' EXIT HUP INT TERM
if [ -n "${WIX_WINE_DOTNET:-}" ]; then
    wine "$WIX_WINE_DOTNET" "$(winepath -w "$WIX_WINE_DLL")" build -arch x64 \
        -ext "$(winepath -w "$WIX_UI_EXTENSION")" \
        -d "ExePath=$(winepath -w "$EXE")" -d "RootDir=$(winepath -w "$ROOT")" \
        "$(winepath -w "$SCRIPT_DIR/installer.wxs")" \
        -pdbtype none -o "$(winepath -w "$STAGING/Pong-76-Setup.msi")"
else
    "$WIX" build -arch x64 -ext WixToolset.UI.wixext \
        -d "ExePath=$EXE" -d "RootDir=$ROOT" \
        "$SCRIPT_DIR/installer.wxs" -pdbtype none -o "$STAGING/Pong-76-Setup.msi"
fi

cp "$EXE" "$STAGING/pong76.exe"
cp "$ROOT/assets/pong76-icon.ico" "$STAGING/pong76.ico"
cp "$ROOT/assets/Righteous-OFL.txt" "$STAGING/Righteous-OFL.txt"
(
    cd "$STAGING"
    zip -q portable.zip pong76.exe pong76.ico Righteous-OFL.txt
)
cp "$STAGING/Pong-76-Setup.msi" "$ROOT/dist/Pong-76-Setup.msi"
cp "$STAGING/portable.zip" "$ROOT/dist/Pong-76-Portable.zip"
printf 'Created %s/dist/Pong-76-Setup.msi and Pong-76-Portable.zip\n' "$ROOT"
