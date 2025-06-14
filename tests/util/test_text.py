import unittest

from toyotama.util.text import Text


class TestText(unittest.TestCase):
    def test_text(self):
        raw = """
        f1 = 3218973129837
        f2: 3d330fa3cbed11
        f3 : VEVTVFNUUklOR1Nob2dlaG9nZWhvZ2VmdWdh
        f4 -> VEVTVFNUUklOR1Nob2dlaG9nZWhvZ2VmdWdh 
        3d330fa3cbed11
        """.strip()

        f = Text(raw)
        self.assertEqual(f.readint(), 3218973129837)
        self.assertEqual(f.readhex(), b"=3\x0f\xa3\xcb\xed\x11")
        self.assertEqual(f.readbase64(), b"TESTSTRINGShogehogehogefuga")
        self.assertEqual(f.readhex(), b"=3\x0f\xa3\xcb\xed\x11")

        f.update_pattern(r" *(?P<name>.*?) *[->:] *(?P<value>.*)")
        self.assertEqual(f.readbase64(), b"TESTSTRINGShogehogehogefuga")
