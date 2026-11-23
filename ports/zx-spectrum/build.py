#!/usr/bin/env python3
"""Assemble the Spectrum port and create an auto-loading TAP image."""

import argparse
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


PORT_DIR = Path(__file__).resolve().parent
SOURCE = PORT_DIR / "pong76.asm"
OUTPUT = PORT_DIR / "pong76.tap"
LOADING_SCREEN = PORT_DIR / "loading.scr"
LOAD_ADDRESS = 30000
SCREEN_ADDRESS = 16384
SCREEN_SIZE = 6912
BASIC_START_LINE = 10
PROGRAM_NAME = b"PONG76    "
SCREEN_NAME = b"PONG76SCR "
CODE_NAME = b"PONG76    "


def basic_number(value: int) -> bytes:
    return (
        str(value).encode("ascii")
        + b"\x0e\x00\x00"
        + struct.pack("<H", value)
        + b"\x00"
    )


def basic_loader() -> bytes:
    line = (
        bytes((0xFD,))
        + basic_number(LOAD_ADDRESS - 1)
        + b":"
        + bytes((0xEF,))
        + b'""'
        + bytes((0xAA,))
        + b":"
        + bytes((0xEF,))
        + b'""'
        + bytes((0xAF,))
        + b":"
        + bytes((0xF9,))
        + bytes((0xC0,))
        + basic_number(LOAD_ADDRESS)
        + b"\r"
    )
    return struct.pack(">H", BASIC_START_LINE) + struct.pack("<H", len(line)) + line


def program_header(program: bytes) -> bytes:
    return (
        b"\x00\x00"
        + PROGRAM_NAME
        + struct.pack("<HHH", len(program), BASIC_START_LINE, len(program))
    )


def code_header(code: bytes, *, name: bytes = CODE_NAME, address: int = LOAD_ADDRESS) -> bytes:
    return (
        b"\x00\x03"
        + name
        + struct.pack("<HHH", len(code), address, 32768)
    )


def tap_block(data: bytes) -> bytes:
    checksum = 0
    for byte in data:
        checksum ^= byte
    block = data + bytes((checksum,))
    return struct.pack("<H", len(block)) + block


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--assembler",
        default="pasmo",
        help="Pasmo executable (default: pasmo)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help=f"output TAP file (default: {OUTPUT})",
    )
    args = parser.parse_args()

    assembler = shutil.which(args.assembler)
    if assembler is None:
        parser.error(
            f"assembler not found: {args.assembler}; install Pasmo or use --assembler"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        binary = Path(temp_dir) / "pong76.bin"
        subprocess.run(
            [assembler, "--bin", str(SOURCE), str(binary)],
            check=True,
            cwd=PORT_DIR,
        )
        code = binary.read_bytes()

    if len(code) > 65535:
        parser.error(f"assembled code is too large for a TAP code block: {len(code)}")

    screen = LOADING_SCREEN.read_bytes()
    if len(screen) != SCREEN_SIZE:
        parser.error(f"loading screen must be {SCREEN_SIZE} bytes, got {len(screen)}")

    loader = basic_loader()
    tape = (
        tap_block(program_header(loader))
        + tap_block(b"\xff" + loader)
        + tap_block(code_header(screen, name=SCREEN_NAME, address=SCREEN_ADDRESS))
        + tap_block(b"\xff" + screen)
        + tap_block(code_header(code))
        + tap_block(b"\xff" + code)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(tape)
    print(f"Wrote {args.output} (BASIC loader, loading screen, {len(code)} bytes of machine code)")


if __name__ == "__main__":
    main()
