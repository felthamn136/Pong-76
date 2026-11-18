#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
TARGET="x86_64-pc-windows-gnu"
APP_VERSION="0.1.0"
MAKENSIS="${MAKENSIS:-makensis}"

if ! command -v x86_64-w64-mingw32-gcc >/dev/null 2>&1; then
    printf 'The x86_64 MinGW-w64 compiler is required to build the Windows executable.\n' >&2
    exit 1
fi

if ! command -v "$MAKENSIS" >/dev/null 2>&1; then
    printf 'NSIS was not found; install it or set MAKENSIS to its executable path.\n' >&2
    exit 1
fi

if ! rustup target list --installed | grep -Fxq "$TARGET"; then
    printf 'Rust target %s is not installed; run: rustup target add %s\n' "$TARGET" "$TARGET" >&2
    exit 1
fi

cargo build --manifest-path "$ROOT/Cargo.toml" --release --target "$TARGET"
mkdir -p "$ROOT/dist"
cd "$ROOT"
"$MAKENSIS" -NOCD -V2 "-DAPP_VERSION=$APP_VERSION" "$SCRIPT_DIR/installer.nsi"
printf 'Created %s/dist/Pong-76-Setup.exe\n' "$ROOT"
