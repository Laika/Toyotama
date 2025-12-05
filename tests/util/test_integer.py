"""Tests for toyotama.util.integer module."""

import pytest

from toyotama.util.integer import (
    Int,
    Int8,
    Int16,
    Int32,
    Int64,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
)


class TestInt:
    """Tests for Int class."""

    def test_unsigned_32bit_basic(self):
        """Test basic unsigned 32-bit integer."""
        x = Int(0x12345678, bits=32, signed=False)
        assert x.x == 0x12345678

    def test_unsigned_32bit_overflow(self):
        """Test unsigned 32-bit integer overflow wraps correctly."""
        x = Int(0xFFFFFFFF, bits=32, signed=False)
        assert x.x == 0xFFFFFFFF
        x.x = 0x100000000
        assert x.x == 0  # Should wrap

    def test_signed_32bit_positive(self):
        """Test signed 32-bit positive integer."""
        x = Int(100, bits=32, signed=True)
        assert x.x == 100

    def test_signed_32bit_negative(self):
        """Test signed 32-bit negative integer."""
        x = Int(-1, bits=32, signed=True)
        assert x.x == -1

    def test_signed_32bit_from_unsigned(self):
        """Test signed interpretation of unsigned value."""
        x = Int(0xFFFFFFFF, bits=32, signed=True)
        assert x.x == -1

    def test_signed_8bit_boundary(self):
        """Test signed 8-bit boundary values."""
        x = Int(127, bits=8, signed=True)
        assert x.x == 127

        x = Int(128, bits=8, signed=True)
        assert x.x == -128

        x = Int(255, bits=8, signed=True)
        assert x.x == -1

    def test_addition(self):
        """Test integer addition."""
        a = Int(10, bits=32, signed=False)
        b = Int(20, bits=32, signed=False)
        c = a + b
        assert c.x == 30

    def test_subtraction(self):
        """Test integer subtraction."""
        a = Int(30, bits=32, signed=False)
        b = Int(10, bits=32, signed=False)
        c = a - b
        assert c.x == 20

    def test_multiplication(self):
        """Test integer multiplication."""
        a = Int(5, bits=32, signed=False)
        b = Int(6, bits=32, signed=False)
        c = a * b
        assert c.x == 30

    def test_to_bytes(self):
        """Test conversion to bytes."""
        x = Int(0x12345678, bits=32, signed=False)
        assert x.to_bytes("big") == b"\x12\x34\x56\x78"
        assert x.to_bytes("little") == b"\x78\x56\x34\x12"


class TestUInt8:
    """Tests for UInt8 type alias."""

    def test_basic(self):
        """Test UInt8 basic operation."""
        x = UInt8(255)
        assert x.x == 255
        assert x.bits == 8
        assert x.signed is False

    def test_overflow(self):
        """Test UInt8 overflow."""
        x = UInt8(256)
        assert x.x == 0


class TestUInt16:
    """Tests for UInt16 type alias."""

    def test_basic(self):
        """Test UInt16 basic operation."""
        x = UInt16(0xFFFF)
        assert x.x == 0xFFFF
        assert x.bits == 16
        assert x.signed is False


class TestUInt32:
    """Tests for UInt32 type alias."""

    def test_basic(self):
        """Test UInt32 basic operation."""
        x = UInt32(0xDEADBEEF)
        assert x.x == 0xDEADBEEF
        assert x.bits == 32
        assert x.signed is False


class TestUInt64:
    """Tests for UInt64 type alias."""

    def test_basic(self):
        """Test UInt64 basic operation."""
        x = UInt64(0xDEADBEEFCAFEBABE)
        assert x.x == 0xDEADBEEFCAFEBABE
        assert x.bits == 64
        assert x.signed is False


class TestInt8:
    """Tests for Int8 type alias."""

    def test_basic(self):
        """Test Int8 basic operation."""
        x = Int8(-1)
        assert x.x == -1
        assert x.bits == 8
        assert x.signed is True

    def test_positive(self):
        """Test Int8 positive value."""
        x = Int8(127)
        assert x.x == 127


class TestInt16:
    """Tests for Int16 type alias."""

    def test_basic(self):
        """Test Int16 basic operation."""
        x = Int16(-1000)
        assert x.x == -1000
        assert x.bits == 16
        assert x.signed is True


class TestInt32:
    """Tests for Int32 type alias."""

    def test_basic(self):
        """Test Int32 basic operation."""
        x = Int32(-100000)
        assert x.x == -100000
        assert x.bits == 32
        assert x.signed is True


class TestInt64:
    """Tests for Int64 type alias."""

    def test_basic(self):
        """Test Int64 basic operation."""
        x = Int64(-1)
        assert x.x == -1
        assert x.bits == 64
        assert x.signed is True
