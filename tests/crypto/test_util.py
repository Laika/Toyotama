import random

import pytest
from Crypto.Util.number import getPrime

from toyotama.crypto.util import (
    babystep_giantstep,
    chinese_remainder,
    extended_gcd,
    int_to_bytes,
    inverse,
    is_prime,
    is_square,
    mod_sqrt,
    next_prime,
    solve_quadratic_equation,
    xor,
)


class TestModSqrt:
    """Tests for mod_sqrt function."""

    def test_mod_sqrt_basic(self):
        """Test mod_sqrt with known values."""
        p = getPrime(1024)
        x = random.getrandbits(1024)
        xx = x * x % p
        X = mod_sqrt(xx, p)
        ok = x == X or x == p - X
        assert ok


class TestChineseRemainder:
    """Tests for chinese_remainder function."""

    def test_chinese_remainder_basic(self):
        """Test chinese_remainder with random values."""
        y = random.getrandbits(1024)
        m = [random.getrandbits(512) for _ in range(4)]
        a = [y % x for x in m]
        A, M = chinese_remainder(a, m)
        assert A % M == y % M

    def test_chinese_remainder_simple(self):
        """Test chinese_remainder with simple known values."""
        # x = 2 (mod 3), x = 3 (mod 5), x = 2 (mod 7)
        # Solution: x = 23 (mod 105)
        a = [2, 3, 2]
        m = [3, 5, 7]
        A, M = chinese_remainder(a, m)
        assert M == 105
        assert A % 3 == 2
        assert A % 5 == 3
        assert A % 7 == 2


class TestSolveQuadraticEquation:
    """Tests for solve_quadratic_equation function."""

    def test_quadratic_simple(self):
        """Test with simple quadratic: x^2 - 5x + 6 = 0 -> x = 2, 3."""
        # a=1, b=-5, c=6
        x1, x2 = solve_quadratic_equation(1, -5, 6)
        solutions = {x1, x2}
        assert 2 in solutions
        assert 3 in solutions

    def test_quadratic_perfect_square(self):
        """Test with perfect square: x^2 - 4x + 4 = 0 -> x = 2."""
        x1, x2 = solve_quadratic_equation(1, -4, 4)
        assert x1 == 2
        assert x2 == 2

    def test_quadratic_larger_coefficients(self):
        """Test with larger coefficients: 2x^2 - 10x + 12 = 0 -> x = 2, 3."""
        x1, x2 = solve_quadratic_equation(2, -10, 12)
        solutions = {x1, x2}
        assert 2 in solutions
        assert 3 in solutions


class TestExtendedGcd:
    """Tests for extended_gcd function."""

    def test_extended_gcd_coprime(self):
        """Test extended_gcd with coprime numbers."""
        x, y, g = extended_gcd(17, 13)
        assert g == 1
        assert 17 * x + 13 * y == g

    def test_extended_gcd_common_factor(self):
        """Test extended_gcd with common factor."""
        x, y, g = extended_gcd(12, 18)
        assert g == 6
        assert 12 * x + 18 * y == g


class TestIsPrime:
    """Tests for is_prime function."""

    def test_is_prime_known_primes(self):
        """Test is_prime with known primes."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in primes:
            assert is_prime(p), f"{p} should be prime"

    def test_is_prime_known_composites(self):
        """Test is_prime with known composites."""
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for c in composites:
            assert not is_prime(c), f"{c} should not be prime"

    def test_is_prime_edge_cases(self):
        """Test is_prime with edge cases."""
        assert not is_prime(0)
        assert not is_prime(1)
        assert is_prime(2)


class TestNextPrime:
    """Tests for next_prime function."""

    def test_next_prime_basic(self):
        """Test next_prime with basic values."""
        assert next_prime(1) == 2
        assert next_prime(2) == 3
        assert next_prime(4) == 5
        assert next_prime(10) == 11

    def test_next_prime_from_prime(self):
        """Test next_prime starting from a prime."""
        assert next_prime(7) == 11


class TestXor:
    """Tests for xor function."""

    def test_xor_two_bytes(self):
        """Test xor with two byte strings."""
        result = xor(b"\x00\x01\x02", b"\xff\xfe\xfd")
        assert result == b"\xff\xff\xff"

    def test_xor_multiple_bytes(self):
        """Test xor with multiple byte strings."""
        result = xor(b"\xff", b"\xff", b"\xff")
        assert result == b"\xff"

    def test_xor_empty(self):
        """Test xor with no arguments."""
        result = xor()
        assert result == b""


class TestIntToBytes:
    """Tests for int_to_bytes function."""

    def test_int_to_bytes_basic(self):
        """Test int_to_bytes with basic values."""
        assert int_to_bytes(0x41) == b"A"
        assert int_to_bytes(0x4142) == b"AB"

    def test_int_to_bytes_big_endian(self):
        """Test int_to_bytes with big endian (default)."""
        assert int_to_bytes(0x0102, "big") == b"\x01\x02"

    def test_int_to_bytes_little_endian(self):
        """Test int_to_bytes with little endian."""
        assert int_to_bytes(0x0102, "little") == b"\x02\x01"


class TestInverse:
    """Tests for inverse function."""

    def test_inverse_basic(self):
        """Test modular inverse."""
        assert inverse(3, 7) == 5  # 3 * 5 = 15 = 1 (mod 7)
        assert inverse(2, 11) == 6  # 2 * 6 = 12 = 1 (mod 11)


class TestIsSquare:
    """Tests for is_square function."""

    def test_is_square_perfect(self):
        """Test is_square with perfect squares."""
        assert is_square(0)
        assert is_square(1)
        assert is_square(4)
        assert is_square(9)
        assert is_square(16)
        assert is_square(100)

    def test_is_square_non_perfect(self):
        """Test is_square with non-perfect squares."""
        assert not is_square(2)
        assert not is_square(3)
        assert not is_square(5)
        assert not is_square(10)
