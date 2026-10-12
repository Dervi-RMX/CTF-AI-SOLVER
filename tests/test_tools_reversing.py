"""
Unit tests for Reversing tools in CTF-AI Solver Pro.
"""

from pathlib import Path
import struct
import tempfile
import unittest

from ctf_ai.tools.reversing import (
    BinaryHeaderInspectorTool,
    SectionEntropyInspectorTool,
    ReversingToolsDetectorTool,
)


class TestReversingTools(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.headers_tool = BinaryHeaderInspectorTool()
        self.entropy_tool = SectionEntropyInspectorTool()
        self.detector_tool = ReversingToolsDetectorTool()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_elf_header_inspection(self):
        elf_path = Path(self.tmp_dir.name) / "test_prog.elf"
        # Create minimal 64-bit ELF header
        # 0x00: \x7fELF
        # 0x04: 2 (64-bit)
        # 0x05: 1 (Little Endian)
        # 0x06: 1 (EV_CURRENT)
        # 0x07..0x0F: padding
        # 0x10: e_type (2 = ET_EXEC), e_machine (62 = x86-64)
        # 0x18: e_entry (0x401000)
        e_ident = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
        e_type_machine = struct.pack("<HH", 2, 62)
        e_version = struct.pack("<I", 1)
        e_entry = struct.pack("<Q", 0x401000)
        header_data = e_ident + e_type_machine + e_version + e_entry + b"\x00" * 64

        elf_path.write_bytes(header_data)

        res = self.headers_tool.run(file_path=str(elf_path))
        self.assertTrue(res.success)
        self.assertEqual(res.data["format"], "ELF (Linux)")
        self.assertEqual(res.data["architecture"], "64-bit")
        self.assertEqual(res.data["machine"], "x86-64 (AMD64)")
        self.assertEqual(res.data["entry_point"], "0x401000")

    def test_pe_header_inspection(self):
        pe_path = Path(self.tmp_dir.name) / "test_prog.exe"
        # Create minimal PE header
        # DOS header: 'MZ', offset 0x3C points to PE header
        dos_header = bytearray(64)
        dos_header[:2] = b"MZ"
        struct.pack_into("<I", dos_header, 0x3C, 64)  # e_lfanew = 64

        # PE signature + COFF header
        pe_sig = b"PE\x00\x00"
        coff_header = struct.pack("<HHI", 0x8664, 5, 0x12345678) + b"\x00" * 12
        full_data = bytes(dos_header) + pe_sig + coff_header + b"\x00" * 128
        pe_path.write_bytes(full_data)

        res = self.headers_tool.run(file_path=str(pe_path))
        self.assertTrue(res.success)
        self.assertIn("PE", res.data["format"])
        self.assertEqual(res.data["architecture"], "x86-64 (AMD64)")
        self.assertEqual(res.data["sections_count"], 5)

    def test_section_entropy_upx_detection(self):
        bin_path = Path(self.tmp_dir.name) / "packed.bin"
        # High entropy data + UPX signature
        high_entropy_bytes = bytes([i % 256 for i in range(4096)]) + b"UPX0UPX!somecode"
        bin_path.write_bytes(high_entropy_bytes)

        res = self.entropy_tool.run(file_path=str(bin_path))
        self.assertTrue(res.success)
        self.assertTrue(res.data["upx_signature_detected"])
        self.assertIn("UPX", res.data["diagnosis"])

    def test_reversing_tools_detector(self):
        res = self.detector_tool.run()
        self.assertTrue(res.success)
        self.assertIn("strings", res.data)
        self.assertIn("available", res.data["strings"])


if __name__ == "__main__":
    unittest.main()
