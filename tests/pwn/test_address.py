"""Tests for toyotama.pwn.address module."""

import pytest

from toyotama.pwn.address import Address, Addr


class TestAddress:
    """Tests for Address class."""

    def test_basic_creation(self):
        """Test basic address creation."""
        addr = Address(0x400000)
        assert addr.address == 0x400000

    def test_str_representation(self):
        """Test string representation."""
        addr = Address(0x400000)
        assert str(addr) == "0x400000"

    def test_repr(self):
        """Test repr representation."""
        addr = Address(0x400000)
        assert "0x400000" in repr(addr)

    def test_hex(self):
        """Test hex method."""
        addr = Address(0x400000)
        assert addr.hex() == "0x400000"

    def test_addition(self):
        """Test address addition."""
        addr = Address(0x400000)
        result = addr + 0x100
        assert result.address == 0x400100
        assert isinstance(result, Address)

    def test_subtraction_with_int(self):
        """Test address subtraction with int."""
        addr = Address(0x400100)
        result = addr - 0x100
        assert result.address == 0x400000
        assert isinstance(result, Address)

    def test_subtraction_with_address(self):
        """Test address subtraction with another Address."""
        addr1 = Address(0x400100)
        addr2 = Address(0x400000)
        result = addr1 - addr2
        assert result.address == 0x100
        assert isinstance(result, Address)

    def test_iadd(self):
        """Test in-place addition."""
        addr = Address(0x400000)
        addr += 0x100
        assert addr.address == 0x400100

    def test_isub(self):
        """Test in-place subtraction."""
        addr = Address(0x400100)
        addr -= 0x100
        assert addr.address == 0x400000

    def test_lshift(self):
        """Test left shift."""
        addr = Address(0x1)
        result = addr << 4
        assert isinstance(result, Address)

    def test_rshift(self):
        """Test right shift."""
        addr = Address(0x10)
        result = addr >> 4
        assert isinstance(result, Address)

    def test_pack_p64(self):
        """Test pack method with p64."""
        addr = Address(0x400000)
        packed = addr.pack()
        assert packed == b"\x00\x00\x40\x00\x00\x00\x00\x00"

    def test_p8(self):
        """Test p8 method."""
        addr = Address(0x41)
        assert addr.p8() == b"A"

    def test_p16(self):
        """Test p16 method."""
        addr = Address(0x4142)
        assert addr.p16() == b"BA"  # Little endian

    def test_p32(self):
        """Test p32 method."""
        addr = Address(0x41424344)
        assert addr.p32() == b"DCBA"  # Little endian

    def test_p64(self):
        """Test p64 method."""
        addr = Address(0x4142434445464748)
        assert addr.p64() == b"HGFEDCBA"  # Little endian

    def test_u64(self):
        """Test u64 class method."""
        data = b"\x48\x47\x46\x45\x44\x43\x42\x41"
        addr = Address.u64(data)
        assert addr.address == 0x4142434445464748

    def test_u64_short_input(self):
        """Test u64 with short input (padded with zeros)."""
        data = b"\x41\x42"
        addr = Address.u64(data)
        assert addr.address == 0x4241

    def test_addition_invalid_type(self):
        """Test addition with invalid type raises TypeError."""
        addr = Address(0x400000)
        with pytest.raises(TypeError):
            addr + "invalid"  # type: ignore

    def test_subtraction_invalid_type(self):
        """Test subtraction with invalid type raises TypeError."""
        addr = Address(0x400000)
        with pytest.raises(TypeError):
            addr - "invalid"  # type: ignore

    def test_addr_alias(self):
        """Test Addr is alias for Address."""
        assert Addr is Address


class TestAddressDesignIssues:
    """Tests that expose design issues in Address class.

    These tests document known issues with the current implementation.
    """

    @pytest.mark.xfail(reason="Design issue: int inheritance vs mutable state")
    def test_int_inheritance_consistency(self):
        """Test that int value and address attribute stay consistent.

        This test exposes the issue where Address inherits from int (immutable)
        but has a mutable address attribute. After iadd, the int value and
        address attribute diverge.
        """
        addr = Address(0x1000)
        addr += 0x100

        # These should be equal, but they're not due to int immutability
        assert int(addr) == addr.address

    @pytest.mark.xfail(reason="Design issue: abs() in subtraction")
    def test_subtraction_negative_offset(self):
        """Test that subtraction can produce negative offsets.

        Current implementation uses abs(), which prevents negative results.
        This can be problematic when calculating relative offsets.
        """
        addr1 = Address(0x1000)
        addr2 = Address(0x2000)
        result = addr1 - addr2

        # Should be -0x1000, but abs() makes it 0x1000
        assert result.address == -0x1000 or result.address == 0xFFFFFFFFFFFFFFFF - 0x1000 + 1
