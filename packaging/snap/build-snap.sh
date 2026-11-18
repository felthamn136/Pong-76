#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
SNAPDIR="$ROOT/target/snap/Pong76"
OUTPUT="$ROOT/dist"

if ! command -v snap >/dev/null 2>&1; then
    printf 'The snap command is required to build the package.\n' >&2
    exit 1
fi

cargo build --manifest-path "$ROOT/Cargo.toml" --release
mkdir -p \
    "$SNAPDIR/bin" \
    "$SNAPDIR/lib/x86_64-linux-gnu" \
    "$SNAPDIR/meta/gui" \
    "$OUTPUT"
cp "$ROOT/target/release/pong76" "$SNAPDIR/bin/pong76"
cp "$SCRIPT_DIR/snap.yaml" "$SNAPDIR/meta/snap.yaml"
cp "$SCRIPT_DIR/pong-76.desktop" "$SNAPDIR/meta/gui/pong-76.desktop"
cp "$ROOT/assets/pong76-logo.png" "$SNAPDIR/meta/gui/pong76.png"

for library in libudev.so.1 libasound.so.2 libgcc_s.so.1; do
    library_path="$(ldconfig -p | awk -v library="$library" '$1 == library && /x86-64/ { print $NF; exit }')"
    if [ -z "$library_path" ]; then
        printf 'Required runtime library was not found: %s\n' "$library" >&2
        exit 1
    fi
    cp -L "$library_path" "$SNAPDIR/lib/x86_64-linux-gnu/$library"
done

chmod a+rx "$SNAPDIR/bin/pong76"
chmod a+r "$SNAPDIR/meta/snap.yaml" "$SNAPDIR/meta/gui/"*
snap pack --check-skeleton "$SNAPDIR"
snap pack --filename=pong-76_0.1.0_amd64.snap "$SNAPDIR" "$OUTPUT"
printf 'Created %s/pong-76_0.1.0_amd64.snap\n' "$OUTPUT"
