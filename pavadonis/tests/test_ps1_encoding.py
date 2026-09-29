"""Windows PowerShell 5.1 UTF-8 failu bez BOM lasa kā ANSI; latviešu teksts tad salauž parseri."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Ps1EncodingTest(unittest.TestCase):
    def test_all_ps1_are_utf8_with_bom(self):
        files = sorted(ROOT.rglob("*.ps1"))
        self.assertTrue(files, "nav atrasts neviens .ps1")
        for f in files:
            with self.subTest(f.relative_to(ROOT).as_posix()):
                data = f.read_bytes()
                self.assertTrue(data.startswith(b"\xef\xbb\xbf"), "trūkst UTF-8 BOM")
                data[3:].decode("utf-8")  # jābūt derīgam UTF-8


if __name__ == "__main__":
    unittest.main()
