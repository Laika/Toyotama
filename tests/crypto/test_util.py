import random
import unittest

from Crypto.Util.number import getPrime

from toyotama.crypto.util import chinese_remainder, mod_sqrt


class UtilTestCase(unittest.TestCase):
    def test_mod_sqrt(self):
        p = getPrime(1024)
        x = random.getrandbits(1024)
        xx = x * x % p
        X = mod_sqrt(xx, p)
        ok = x == X or x == p - X

        self.assertTrue(ok)

    def test_chinese_remainder(self):
        y = random.getrandbits(1024)
        m = [random.getrandbits(512) for _ in range(4)]
        a = [y % x for x in m]
        A, M = chinese_remainder(a, m)
        self.assertEqual(A % M, y)
