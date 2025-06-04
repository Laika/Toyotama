import unittest

from toyotama.util.integer import UInt8, UChar, UInt16, UInt32, UInt64, Int8, Int16, Int32, Int64


class IntegerInstantiationTestCase(unittest.TestCase):
    def test_instantiation(self):
        for cls in [UInt8, UChar, UInt16, UInt32, UInt64, Int8, Int16, Int32, Int64]:
            cls(1)

