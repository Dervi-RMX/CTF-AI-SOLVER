"""
Unit tests for Digital Forensics tools in CTF-AI Solver Pro.
"""

import os
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from ctf_ai.tools.forensics import (
    MagicBytesInspectorTool,
    DeepStringsTool,
    ZipInspectorTool,
    PcapParserTool,
)


class TestForensicsTools(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.magic_tool = MagicBytesInspectorTool()
        self.strings_tool = DeepStringsTool()
        self.zip_tool = ZipInspectorTool()
        self.pcap_tool = PcapParserTool()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_magic_bytes_png(self):
        png_path = Path(self.tmp_dir.name) / "sample.png"
        png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        png_path.write_bytes(png_header)

        res = self.magic_tool.run(file_path=str(png_path))
        self.assertTrue(res.success)
        self.assertIn("PNG Image", res.data["detected_type"])

    def test_magic_bytes_elf(self):
        elf_path = Path(self.tmp_dir.name) / "sample.elf"
        elf_header = b"\x7fELF\x02\x01\x01\x00"
        elf_path.write_bytes(elf_header)

        res = self.magic_tool.run(file_path=str(elf_path))
        self.assertTrue(res.success)
        self.assertIn("ELF Executable", res.data["detected_type"])

    def test_deep_strings_ascii_and_utf16(self):
        bin_path = Path(self.tmp_dir.name) / "test.bin"
        ascii_flag = b"SuperSecret CTF{ascii_flag_found} EndPart\x00\x00"
        utf16_flag = "CTF{utf16_wide_flag}".encode("utf-16-le")
        bin_path.write_bytes(ascii_flag + b"\xff\xff" + utf16_flag)

        res = self.strings_tool.run(file_path=str(bin_path), min_len=4)
        self.assertTrue(res.success)
        potential = res.data["potential_flags"]
        self.assertTrue(any("CTF{ascii_flag_found}" in f for f in potential))
        self.assertTrue(any("CTF{utf16_wide_flag}" in f for f in potential))

    def test_zip_inspector_normal(self):
        zip_path = Path(self.tmp_dir.name) / "archive.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("notes.txt", "Some text")
            zf.writestr("secret.flag", "CTF{zip_flag}")

        res = self.zip_tool.run(file_path=str(zip_path))
        self.assertTrue(res.success)
        self.assertEqual(res.data["file_count"], 2)
        self.assertEqual(len(res.data["security_warnings"]), 0)

    def test_zip_inspector_path_traversal_detection(self):
        zip_path = Path(self.tmp_dir.name) / "traversal.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("../../etc/passwd", "root:x:0:0:::")

        res = self.zip_tool.run(file_path=str(zip_path))
        self.assertTrue(res.success)
        self.assertTrue(any("Path Traversal" in w for w in res.data["security_warnings"]))

    def test_pcap_parser(self):
        # Create a valid minimal synthetic PCAP file (Little Endian)
        pcap_path = Path(self.tmp_dir.name) / "test.pcap"
        # Global Header: 24 bytes
        # magic_number (0xd4c3b2a1), v_major(2), v_minor(4), thiszone(0), sigfigs(0), snaplen(65535), network(1 - Ethernet)
        gh = struct.pack("<IHHiIII", 0xa1b2c3d4 ^ 0, 2, 4, 0, 0, 65535, 1)
        # We need magic b"\xd4\xc3\xb2\xa1"
        gh = b"\xd4\xc3\xb2\xa1" + struct.pack("<HHiIII", 2, 4, 0, 0, 65535, 1)

        # Packet 1 with flag in payload
        # Packet header: ts_sec(0), ts_usec(0), incl_len, orig_len
        payload = b"\x00" * 12 + b"\x08\x00" + b"\x00" * 12 + bytes([192, 168, 1, 10, 10, 0, 0, 1]) + b"flag{pcap_packet_intercepted}"
        pkt_hdr = struct.pack("<IIII", 1000, 500, len(payload), len(payload))

        pcap_path.write_bytes(gh + pkt_hdr + payload)

        res = self.pcap_tool.run(file_path=str(pcap_path))
        self.assertTrue(res.success)
        self.assertEqual(res.data["packets_analyzed"], 1)
        self.assertTrue(any("flag{pcap_packet_intercepted}" in f for f in res.data["potential_flags"]))


if __name__ == "__main__":
    unittest.main()
