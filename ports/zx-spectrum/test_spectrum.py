#!/usr/bin/env python3
"""Focused Z80 regressions; requires Pasmo and the libz80ex runtime."""

import ctypes
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PORT_DIR = Path(__file__).resolve().parent
PTR = ctypes.c_void_p
BYTE = ctypes.c_ubyte
WORD = ctypes.c_uint16
MREAD = ctypes.CFUNCTYPE(BYTE, PTR, WORD, ctypes.c_int, PTR)
MWRITE = ctypes.CFUNCTYPE(None, PTR, WORD, BYTE, PTR)
PREAD = ctypes.CFUNCTYPE(BYTE, PTR, WORD, PTR)
PWRITE = ctypes.CFUNCTYPE(None, PTR, WORD, BYTE, PTR)
IREAD = ctypes.CFUNCTYPE(BYTE, PTR, PTR)


def bitmap_address(x, y):
    return ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (x >> 3)


class TapeTests(unittest.TestCase):
    def test_autostart_loader_and_screen_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            tape = Path(temp) / "pong76.tap"
            subprocess.run(
                [sys.executable, str(PORT_DIR / "build.py"), "--output", str(tape)],
                check=True,
                capture_output=True,
            )
            data = tape.read_bytes()

        blocks = []
        offset = 0
        while offset < len(data):
            length = struct.unpack_from("<H", data, offset)[0]
            offset += 2
            block = data[offset:offset + length]
            self.assertEqual(len(block), length)
            checksum = 0
            for byte in block:
                checksum ^= byte
            self.assertEqual(checksum, 0)
            blocks.append(block)
            offset += length
        self.assertEqual(offset, len(data))
        self.assertEqual(len(blocks), 6)
        self.assertEqual([block[0] for block in blocks], [0, 255, 0, 255, 0, 255])

        # The BASIC line is byte-for-byte identical to zmakebas output.
        loader = bytes.fromhex(
            "000a2500fd32393939390e00002f75003aef2222aa3a"
            "ef2222af3af9c033303030300e00003075000d"
        )
        self.assertEqual(blocks[1][1:-1], loader)
        self.assertEqual(struct.unpack_from("<HHH", blocks[0], 12), (len(loader), 10, len(loader)))
        self.assertEqual(blocks[2][1:12], b"\x03PONG76SCR ")
        self.assertEqual(struct.unpack_from("<HHH", blocks[2], 12), (6912, 16384, 32768))
        self.assertEqual(blocks[3][1:-1], (PORT_DIR / "loading.scr").read_bytes())
        self.assertEqual(blocks[4][1:12], b"\x03PONG76    ")
        self.assertEqual(struct.unpack_from("<HHH", blocks[4], 12), (len(blocks[5]) - 2, 30000, 32768))
        self.assertTrue(blocks[5][1:-1].endswith((PORT_DIR / "menu.scr").read_bytes()))


class SpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = ctypes.CDLL("libz80ex.so.1")
        cls.lib.z80ex_create.restype = PTR
        cls.lib.z80ex_create.argtypes = [MREAD, PTR, MWRITE, PTR, PREAD, PTR, PWRITE, PTR, IREAD, PTR]
        cls.lib.z80ex_destroy.argtypes = [PTR]
        cls.lib.z80ex_set_reg.argtypes = [PTR, ctypes.c_int, WORD]
        cls.lib.z80ex_get_reg.argtypes = [PTR, ctypes.c_int]
        cls.lib.z80ex_get_reg.restype = WORD
        cls.lib.z80ex_step.argtypes = [PTR]
        cls.lib.z80ex_step.restype = ctypes.c_int
        with tempfile.TemporaryDirectory() as temp:
            binary = Path(temp) / "pong76.bin"
            symbols = Path(temp) / "pong76.sym"
            subprocess.run(
                ["pasmo", "--bin", "pong76.asm", str(binary), str(symbols)],
                cwd=PORT_DIR,
                check=True,
            )
            cls.binary = binary.read_bytes()
            cls.symbols = {
                match.group(1): int(match.group(2), 16)
                for line in symbols.read_text().splitlines()
                if (match := re.fullmatch(r"(\w+)\s+EQU\s+([0-9A-F]+)H", line))
            }

    def setUp(self):
        self.memory = (BYTE * 65536)()
        self.memory[30000:30000 + len(self.binary)] = self.binary
        self.keys = {}
        self.writes = []
        self.write_times = []
        self.elapsed = 0
        self.callbacks = (
            MREAD(lambda cpu, address, m1, data: self.memory[address]),
            MWRITE(lambda cpu, address, value, data: self.write_memory(address, value)),
            PREAD(lambda cpu, port, data: self.read_port(port)),
            PWRITE(lambda cpu, port, value, data: self.write_port(port, value)),
            IREAD(lambda cpu, data: 255),
        )
        self.cpu = self.lib.z80ex_create(
            self.callbacks[0], None, self.callbacks[1], None, self.callbacks[2], None,
            self.callbacks[3], None, self.callbacks[4], None,
        )
        self.addCleanup(self.lib.z80ex_destroy, self.cpu)

    def write_memory(self, address, value):
        self.memory[address] = value

    def read_port(self, port):
        value = self.keys.get(port, 255)
        return value() if callable(value) else value

    def write_port(self, port, value):
        self.writes.append((port, value))
        self.write_times.append(self.elapsed)

    def set_var(self, name, value):
        self.memory[self.symbols[name]] = value & 255

    def get_var(self, name):
        return self.memory[self.symbols[name]]

    def call(self, name):
        self.memory[0xF000:0xF002] = (0, 1)
        self.lib.z80ex_set_reg(self.cpu, 11, 0xF000)
        self.lib.z80ex_set_reg(self.cpu, 10, self.symbols[name])
        self.elapsed = 0
        for _ in range(100000):
            if self.lib.z80ex_get_reg(self.cpu, 10) == 0x0100:
                return self.elapsed
            self.elapsed += self.lib.z80ex_step(self.cpu)
        self.fail(f"{name} did not return")

    def test_ball_bitmap_and_erasure(self):
        for y in (32, 63, 64, 127, 128, 172):
            for x in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 127, 128, 129, 247, 248, 249):
                with self.subTest(x=x, y=y):
                    self.set_var("BALL_X", x)
                    self.set_var("BALL_Y", y)
                    self.call("DRAW_BALL")
                    expected = bytearray(6144)
                    for py in range(y - 1, y + 3):
                        for px in range(x - 1, x + 3):
                            expected[bitmap_address(px, py)] |= 128 >> (px & 7)
                    self.assertEqual(bytes(self.memory[16384:22528]), expected)
                    self.call("DRAW_BALL")
                    self.assertFalse(any(self.memory[16384:22528]))

    def test_ball_bounces_before_touching_bottom_wall(self):
        self.set_var("BALL_X", 128)
        self.set_var("BALL_Y", 171)
        self.set_var("BALL_VX", 4)
        self.set_var("BALL_VY", 2)
        self.call("MOVE_BALL")
        self.assertEqual((self.get_var("BALL_Y"), self.get_var("BALL_VY")), (172, 254))
        self.call("DRAW_WALLS")
        before = bytes(self.memory[16384:22528])
        self.call("DRAW_BALL")
        for x in range(0, 256, 8):
            address = bitmap_address(x, 175)
            self.assertEqual(self.memory[16384 + address], before[address])
        self.call("DRAW_BALL")
        self.assertEqual(bytes(self.memory[16384:22528]), before)

    def test_paddle_bitmap_and_collision_edges(self):
        for large in (0, 1):
            self.set_var("PADDLE_LARGE", large)
            self.call("APPLY_SETTINGS")
            half = 18 if large else 12
            for side, x, vx, ball_x in (("LEFT", 24, -4, 32), ("RIGHT", 229, 4, 223)):
                for center in (32 + half, 174 - half):
                    with self.subTest(large=large, side=side, center=center):
                        self.set_var(side + "_Y", center)
                        self.call("DRAW_" + side + "_PADDLE")
                        expected = bytearray(6144)
                        for y in range(center - half, center + half):
                            for px in range(x, x + 4):
                                expected[bitmap_address(px, y)] |= 128 >> (px & 7)
                        self.assertEqual(bytes(self.memory[16384:22528]), expected)
                        self.call("DRAW_" + side + "_PADDLE")
                        self.assertFalse(any(self.memory[16384:22528]))
                self.set_var(side + "_Y", 96)
                for difference in (-half - 3, -half - 2, half, half + 1):
                    with self.subTest(large=large, side=side, difference=difference):
                        self.set_var("BALL_X", ball_x)
                        self.set_var("BALL_Y", 96 + difference)
                        self.set_var("BALL_VX", vx)
                        self.set_var("BALL_VY", 0)
                        self.call("MOVE_BALL")
                        hits = -half - 2 <= difference <= half
                        self.assertEqual(self.get_var("BALL_VX"), (-vx if hits else vx) & 255)
                        if hits:
                            self.assertEqual(self.get_var("BALL_X"), 29 if side == "LEFT" else 226)

    def test_menu_music_loops_and_stops_on_space(self):
        melody = bytes(self.memory[self.symbols["MENU_MELODY"]:self.symbols["MENU_MELODY"] + 32])
        overhead = sum(self.call(name) for name in (
            "SELECT_MODE", "SELECT_SETTINGS", "HIGHLIGHT_MENU", "SPACE_PRESSED"
        ))
        frequencies = {}
        for frame in range(128):
            self.writes.clear()
            self.write_times.clear()
            ticks = self.call("MENU_MUSIC")
            if melody[frame // 4] and frame % 4 < 3:
                self.assertEqual([value for _, value in self.writes], [16, 0] * 8)
                frequencies[frame // 4] = 3_500_000 / (self.write_times[2] - self.write_times[0])
                self.assertLess(ticks + overhead, 69888)
            else:
                self.assertFalse(self.writes)
        self.assertEqual((self.get_var("MENU_NOTE"), self.get_var("MENU_TICK")), (0, 0))
        for note, hz in ((0, 523.25), (1, 622.25), (2, 783.99), (6, 1046.5)):
            self.assertLess(abs(frequencies[note] - hz) / hz, 0.03)

        self.memory[self.symbols["MENU_LOOP"]] = 0
        self.memory[self.symbols["MENU_RELEASE"]] = 0
        self.set_var("MENU_NOTE", 15)
        self.set_var("MENU_TICK", 2)
        self.keys[61438] = 251
        space = iter([255] * 6 + [254, 255])
        self.keys[32766] = lambda: next(space)
        self.writes.clear()
        self.call("SHOW_MENU")
        self.assertEqual(self.get_var("GREEN_COLOUR"), 1)
        self.assertEqual((self.get_var("MENU_NOTE"), self.get_var("MENU_TICK")), (1, 2))
        self.assertEqual([value for _, value in self.writes], [16, 0] * 40)


if __name__ == "__main__":
    unittest.main()
