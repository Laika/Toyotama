"""Tests for toyotama.pwn.util module."""

import pytest

from toyotama.pwn.util import fill, p8, p16, p32, p64, u8, u16, u32, u64


class TestPack:
    """Tests for packing functions."""

    def test_p8_positive(self):
        """Test p8 with positive value."""
        assert p8(0x41) == b"A"
        assert p8(0xFF) == b"\xff"

    def test_p8_zero(self):
        """Test p8 with zero."""
        assert p8(0) == b"\x00"

    def test_p8_negative(self):
        """Test p8 with negative value."""
        assert p8(-1) == b"\xff"

    def test_p16_positive(self):
        """Test p16 with positive value."""
        assert p16(0x4142) == b"BA"  # Little endian
        assert p16(0x0001) == b"\x01\x00"

    def test_p16_zero(self):
        """Test p16 with zero."""
        assert p16(0) == b"\x00\x00"

    def test_p16_negative(self):
        """Test p16 with negative value."""
        assert p16(-1) == b"\xff\xff"

    def test_p32_positive(self):
        """Test p32 with positive value."""
        assert p32(0x41424344) == b"DCBA"  # Little endian
        assert p32(0x00000001) == b"\x01\x00\x00\x00"

    def test_p32_zero(self):
        """Test p32 with zero."""
        assert p32(0) == b"\x00\x00\x00\x00"

    def test_p32_negative(self):
        """Test p32 with negative value."""
        assert p32(-1) == b"\xff\xff\xff\xff"

    def test_p64_positive(self):
        """Test p64 with positive value."""
        assert p64(0x4142434445464748) == b"HGFEDCBA"  # Little endian
        assert p64(0x0000000000000001) == b"\x01\x00\x00\x00\x00\x00\x00\x00"

    def test_p64_zero(self):
        """Test p64 with zero."""
        assert p64(0) == b"\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_p64_negative(self):
        """Test p64 with negative value."""
        assert p64(-1) == b"\xff\xff\xff\xff\xff\xff\xff\xff"


class TestUnpack:
    """Tests for unpacking functions."""

    def test_u8_unsigned(self):
        """Test u8 unsigned."""
        assert u8(b"\xff") == 255
        assert u8(b"\x00") == 0
        assert u8(b"\x41") == 0x41

    def test_u8_signed(self):
        """Test u8 signed."""
        assert u8(b"\xff", sign=True) == -1
        assert u8(b"\x7f", sign=True) == 127
        assert u8(b"\x80", sign=True) == -128

    def test_u16_unsigned(self):
        """Test u16 unsigned."""
        assert u16(b"\x01\x00") == 1
        assert u16(b"\xff\xff") == 65535
        assert u16(b"BA") == 0x4142

    def test_u16_signed(self):
        """Test u16 signed."""
        assert u16(b"\xff\xff", sign=True) == -1

    def test_u16_short_input(self):
        """Test u16 with short input (padded with zeros)."""
        assert u16(b"\x01") == 1

    def test_u32_unsigned(self):
        """Test u32 unsigned."""
        assert u32(b"\x01\x00\x00\x00") == 1
        assert u32(b"\xff\xff\xff\xff") == 0xFFFFFFFF
        assert u32(b"DCBA") == 0x41424344

    def test_u32_signed(self):
        """Test u32 signed."""
        assert u32(b"\xff\xff\xff\xff", sign=True) == -1

    def test_u32_short_input(self):
        """Test u32 with short input (padded with zeros)."""
        assert u32(b"\x01\x02") == 0x0201

    def test_u64_unsigned(self):
        """Test u64 unsigned."""
        assert u64(b"\x01\x00\x00\x00\x00\x00\x00\x00") == 1
        assert u64(b"\xff\xff\xff\xff\xff\xff\xff\xff") == 0xFFFFFFFFFFFFFFFF
        assert u64(b"HGFEDCBA") == 0x4142434445464748

    def test_u64_signed(self):
        """Test u64 signed."""
        assert u64(b"\xff\xff\xff\xff\xff\xff\xff\xff", sign=True) == -1

    def test_u64_short_input(self):
        """Test u64 with short input (padded with zeros)."""
        assert u64(b"\x01\x02\x03\x04") == 0x04030201


class TestFill:
    """Tests for fill function."""

    def test_fill_bytes(self):
        """Test fill with bytes."""
        result = fill(5, b"A")
        assert result == b"AAAAA"

    def test_fill_str(self):
        """Test fill with string."""
        result = fill(5, "A")
        assert result == "AAAAA"

    def test_fill_default(self):
        """Test fill with default character."""
        result = fill(5)
        assert result == b"AAAAA"

    def test_fill_zero_length(self):
        """Test fill with zero length."""
        result = fill(0)
        assert result == b""


class TestPackUnpackRoundtrip:
    """Tests for pack/unpack roundtrip consistency."""

    def test_p8_u8_roundtrip(self):
        """Test p8/u8 roundtrip."""
        for val in [0, 1, 127, 128, 255]:
            assert u8(p8(val)) == val

    def test_p16_u16_roundtrip(self):
        """Test p16/u16 roundtrip."""
        for val in [0, 1, 0x7FFF, 0x8000, 0xFFFF]:
            assert u16(p16(val)) == val

    def test_p32_u32_roundtrip(self):
        """Test p32/u32 roundtrip."""
        for val in [0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]:
            assert u32(p32(val)) == val

    def test_p64_u64_roundtrip(self):
        """Test p64/u64 roundtrip."""
        for val in [0, 1, 0x7FFFFFFFFFFFFFFF, 0x8000000000000000, 0xFFFFFFFFFFFFFFFF]:
            assert u64(p64(val)) == val
