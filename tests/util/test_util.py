"""Tests for toyotama.util.util module."""

import pytest

from toyotama.util.util import (
    CyclicString,
    MarkdownTable,
    de_bruijn,
    extract_flag,
    random_string,
)


class TestMarkdownTable:
    """Tests for MarkdownTable class."""

    def test_basic_table(self):
        """Test basic table creation."""
        mt = MarkdownTable(
            header=["Name", "Value"],
            rows=[
                ["foo", "1"],
                ["bar", "2"],
            ],
        )
        result = mt.dump()
        assert "Name" in result
        assert "Value" in result
        assert "foo" in result
        assert "bar" in result

    def test_table_without_header(self):
        """Test table without header."""
        mt = MarkdownTable(
            rows=[
                ["foo", "1"],
                ["bar", "2"],
            ]
        )
        result = mt.dump()
        assert "foo" in result
        assert "bar" in result

    def test_table_alignment(self):
        """Test table alignment."""
        mt = MarkdownTable(
            header=["Short", "LongerHeader"],
            rows=[
                ["a", "b"],
            ],
        )
        result = mt.dump()
        # Should contain properly aligned separators
        assert "|" in result
        assert "-" in result


class TestExtractFlag:
    """Tests for extract_flag function."""

    def test_extract_from_str(self):
        """Test flag extraction from string."""
        text = "The flag is FLAG{test_flag_123} in this text."
        flags = extract_flag(text, head="FLAG{", tail="}")
        assert flags is not None
        assert "FLAG{test_flag_123}" in flags

    def test_extract_from_bytes(self):
        """Test flag extraction from bytes."""
        data = b"The flag is FLAG{test_flag_123} in this data."
        flags = extract_flag(data, head="FLAG{", tail="}")
        assert flags is not None
        assert b"FLAG{test_flag_123}" in flags

    def test_extract_multiple_flags(self):
        """Test extraction of multiple flags."""
        text = "First FLAG{flag1} and second FLAG{flag2} here."
        flags = extract_flag(text, head="FLAG{", tail="}", unique=False)
        assert flags is not None
        assert len(flags) == 2

    def test_extract_unique_flags(self):
        """Test extraction of unique flags only."""
        text = "FLAG{same} and FLAG{same} repeated."
        flags = extract_flag(text, head="FLAG{", tail="}", unique=True)
        assert flags is not None
        assert len(flags) == 1

    def test_no_flag_found(self):
        """Test when no flag is found."""
        text = "No flag here."
        flags = extract_flag(text, head="FLAG{", tail="}")
        assert flags is None

    def test_invalid_type(self):
        """Test with invalid type raises TypeError."""
        with pytest.raises(TypeError):
            extract_flag(123, head="FLAG{", tail="}")  # type: ignore


class TestRandomString:
    """Tests for random_string function."""

    def test_random_string_length(self):
        """Test that random_string returns correct length."""
        result = random_string(10)
        assert len(result) == 10

    def test_random_string_type(self):
        """Test that random_string returns bytes."""
        result = random_string(10)
        assert isinstance(result, bytes)

    def test_random_string_custom_alphabet(self):
        """Test random_string with custom alphabet."""
        alphabet = b"abc"
        result = random_string(100, alphabet=alphabet)
        assert len(result) == 100
        assert all(chr(c).encode() in alphabet for c in result)

    def test_random_string_zero_length(self):
        """Test random_string with zero length."""
        result = random_string(0)
        assert result == b""


class TestDeBruijn:
    """Tests for de_bruijn function."""

    def test_de_bruijn_length(self):
        """Test de_bruijn returns correct length."""
        result = de_bruijn(100, "ABCD")
        assert len(result) == 100

    def test_de_bruijn_uniqueness(self):
        """Test de_bruijn subsequence uniqueness."""
        alphabet = "ABCD"
        n = 4
        result = de_bruijn(256, alphabet, n=n)

        # Check that all n-length substrings are unique
        substrings = set()
        for i in range(len(result) - n + 1):
            substr = result[i : i + n]
            assert substr not in substrings, f"Duplicate found: {substr}"
            substrings.add(substr)


class TestCyclicString:
    """Tests for CyclicString class."""

    def test_generate(self):
        """Test cyclic string generation."""
        cs = CyclicString()
        result = cs.generate(100)
        assert len(result) >= 100

    def test_find_existing(self):
        """Test finding existing subsequence."""
        cs = CyclicString(alphabet="ABCD")
        cs.generate(1000)
        # Find a known subsequence
        substr = cs.generated[10:14]
        pos = cs.find(substr)
        assert pos == 10

    def test_find_nonexistent(self):
        """Test finding non-existent subsequence."""
        cs = CyclicString(alphabet="ABCD")
        cs.generate(100)
        # Characters not in alphabet
        pos = cs.find("XXXX")
        assert pos == -1

    def test_generate_incremental(self):
        """Test that generate returns cached result for smaller length."""
        cs = CyclicString()
        result1 = cs.generate(100)
        result2 = cs.generate(50)
        assert result1 == result2  # Should return same (cached) result
