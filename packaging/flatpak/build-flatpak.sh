#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pong76-flatpak.XXXXXX")"
BUILD_DIR="$WORKDIR/build"
REPO="$WORKDIR/repo"
OUTPUT="$ROOT/dist/Pong-76.flatpak"
APP_ID="io.github.felthamn136.Pong76"
BRANCH="stable"
ARCH="x86_64"
RUNTIME="org.freedesktop.Platform//26.08"

trap 'rm -rf "$WORKDIR"' EXIT HUP INT TERM

if ! command -v flatpak >/dev/null 2>&1; then
    printf 'The flatpak command is required to build the package.\n' >&2
    exit 1
fi

if ! flatpak info "$RUNTIME" >/dev/null 2>&1; then
    printf 'The Flatpak runtime %s must be installed before building.\n' "$RUNTIME" >&2
    exit 1
fi

cargo build --manifest-path "$ROOT/Cargo.toml" --release
flatpak build-init --arch="$ARCH" "$BUILD_DIR" "$APP_ID" "$RUNTIME" "$RUNTIME" "$BRANCH"

install -D -m 0755 "$ROOT/target/release/pong76" "$BUILD_DIR/files/bin/pong76"
install -D -m 0644 "$SCRIPT_DIR/pong76.desktop" \
    "$BUILD_DIR/files/share/applications/$APP_ID.desktop"
install -D -m 0644 "$ROOT/assets/pong76-icon.png" \
    "$BUILD_DIR/files/share/icons/hicolor/512x512/apps/$APP_ID.png"
install -D -m 0644 "$ROOT/assets/Righteous-OFL.txt" \
    "$BUILD_DIR/files/share/doc/pong76/Righteous-OFL.txt"

flatpak build-finish \
    --command=pong76 \
    --share=ipc \
    --socket=x11 \
    --socket=wayland \
    --socket=pulseaudio \
    --device=dri \
    --device=all \
    "$BUILD_DIR"

mkdir -p "$ROOT/dist"
flatpak build-export --arch="$ARCH" "$REPO" "$BUILD_DIR" "$BRANCH"
flatpak build-bundle \
    --arch="$ARCH" \
    --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo \
    "$REPO" "$OUTPUT" "$APP_ID" "$BRANCH"
printf 'Created %s\n' "$OUTPUT"
