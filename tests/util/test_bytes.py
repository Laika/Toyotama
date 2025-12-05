"""Tests for toyotama.util.bytes_ module."""

import pytest

from toyotama.util.bytes_ import Bytes


class TestBytes:
    """Tests for Bytes class."""

    def test_xor_same_length(self):
        """Test XOR with same length bytes."""
        a = Bytes(b"\x00\x01\x02\x03")
        b = Bytes(b"\xff\xfe\xfd\xfc")
        result = a ^ b
        assert result == b"\xff\xff\xff\xff"
        assert isinstance(result, Bytes)

    def test_xor_different_length(self):
        """Test XOR with different length bytes (should warn but work)."""
        a = Bytes(b"\x00\x01\x02")
        b = Bytes(b"\xff\xfe")
        result = a ^ b
        assert result == b"\xff\xff"  # Truncated to shorter length

    def test_rxor(self):
        """Test reverse XOR operation."""
        a = Bytes(b"\x00\x01\x02\x03")
        b = b"\xff\xfe\xfd\xfc"
        result = b ^ a
        assert result == b"\xff\xff\xff\xff"
        assert isinstance(result, Bytes)

    def test_or_concatenation(self):
        """Test OR as concatenation."""
        a = Bytes(b"Hello")
        b = Bytes(b"World")
        result = a | b
        assert result == b"HelloWorld"
        assert isinstance(result, Bytes)

    def test_or_with_bytes(self):
        """Test OR with regular bytes."""
        a = Bytes(b"Hello")
        b = b"World"
        result = a | b
        assert result == b"HelloWorld"
        assert isinstance(result, Bytes)

    def test_ror(self):
        """Test reverse OR operation."""
        a = Bytes(b"World")
        b = b"Hello"
        result = b | a
        assert result == b"HelloWorld"
        assert isinstance(result, Bytes)

    def test_getitem_slice(self):
        """Test slicing returns Bytes."""
        a = Bytes(b"HelloWorld")
        result = a[0:5]
        assert result == b"Hello"
        assert isinstance(result, Bytes)

    def test_getitem_index(self):
        """Test indexing returns int (like standard bytes)."""
        a = Bytes(b"Hello")
        result = a[0]
        assert isinstance(result, int)
        assert result == ord("H")

    def test_to_int(self):
        """Test conversion to integer."""
        a = Bytes(b"\x00\x01")
        assert a.to_int() == 1

        b = Bytes(b"\x01\x00")
        assert b.to_int() == 256

    def test_from_int(self):
        """Test creation from integer."""
        result = Bytes.from_int(256)
        assert result == b"\x01\x00"

        result = Bytes.from_int(1)
        assert result == b"\x01"

    def test_from_int_zero(self):
        """Test from_int(0) returns single null byte."""
        result = Bytes.from_int(0)
        assert result == b"\x00"
        assert len(result) == 1

    def test_to_block(self):
        """Test block splitting."""
        a = Bytes(b"0123456789ABCDEF")
        blocks = a.to_block(block_size=4)
        assert len(blocks) == 4
        assert blocks[0] == b"0123"
        assert blocks[1] == b"4567"
        assert blocks[2] == b"89AB"
        assert blocks[3] == b"CDEF"
        for block in blocks:
            assert isinstance(block, Bytes)

    def test_to_block_default_size(self):
        """Test block splitting with default size (16)."""
        a = Bytes(b"A" * 32)
        blocks = a.to_block()
        assert len(blocks) == 2
        assert all(len(b) == 16 for b in blocks)

    def test_to_base64(self):
        """Test conversion to base64."""
        a = Bytes(b"Hello")
        assert a.to_base64() == "SGVsbG8="

    def test_from_base64_str(self):
        """Test creation from base64 string."""
        result = Bytes.from_base64("SGVsbG8=")
        assert result == b"Hello"
        assert isinstance(result, Bytes)

    def test_from_base64_bytes(self):
        """Test creation from base64 bytes."""
        result = Bytes.from_base64(b"SGVsbG8=")
        assert result == b"Hello"
        assert isinstance(result, Bytes)

    def test_invalid_xor_type(self):
        """Test XOR with invalid type raises TypeError or NotImplementedError."""
        a = Bytes(b"test")
        with pytest.raises((NotImplementedError, TypeError)):
            a ^ 123  # type: ignore

    def test_invalid_or_type(self):
        """Test OR with invalid type raises TypeError or NotImplementedError."""
        a = Bytes(b"test")
        with pytest.raises((NotImplementedError, TypeError)):
            a | 123  # type: ignore

    def test_invalid_ror_type(self):
        """Test reverse OR with invalid type raises NotImplementedError or TypeError."""
        a = Bytes(b"test")
        with pytest.raises((NotImplementedError, TypeError)):
            123 | a  # type: ignore
