import unittest
import random
import gmpy2

from toyotama.crypto.util import chinese_remainder

def generate_prime(bits):
    return int(gmpy2.next_prime(random.getrandbits(bits)))

class UtilTestCase(unittest.TestCase):
    def test_chinese_remainder(self):
        y = random.getrandbits(1024)
        m = [random.getrandbits(512) for _ in range(4)]
        a = [y%x for x in m]
        A, M = chinese_remainder(a, m)
        self.assertEqual(A%M, y) 
