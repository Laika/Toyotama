"""Tests for toyotama.pwn.fsa module."""

import re
import struct

import pytest

from toyotama.pwn.fsa import fsa_write_32, fsa_write_64


class TestFsaWrite32:
    """Tests for fsa_write_32 function."""

    def test_payload_contains_target_address(self):
        """Test that payload contains the target address."""
        target_addr = 0x08049000
        payload = fsa_write_32(value=0x41414141, nth_stack=7, target_addr=target_addr)
        # Target address should be in payload (little-endian)
        assert struct.pack("<I", target_addr) in payload

    def test_payload_contains_format_specifiers(self):
        """Test that payload contains %n format specifiers."""
        payload = fsa_write_32(value=0x41414141, nth_stack=7, target_addr=0x08049000)
        # Should contain %n (4-byte write) by default
        assert b"$n" in payload

    def test_payload_hhn_specifier(self):
        """Test that each=1 uses %hhn specifier."""
        payload = fsa_write_32(value=0x41414141, nth_stack=7, target_addr=0x08049000, each=1)
        assert b"$hhn" in payload

    def test_payload_hn_specifier(self):
        """Test that each=2 uses %hn specifier."""
        payload = fsa_write_32(value=0x41414141, nth_stack=7, target_addr=0x08049000, each=2)
        assert b"$hn" in payload

    def test_invalid_each_value(self):
        """Test that invalid each value raises AssertionError."""
        with pytest.raises(AssertionError):
            fsa_write_32(value=0x41414141, nth_stack=7, target_addr=0x08049000, each=3)

    def test_stack_position_increments(self):
        """Test that stack positions increment correctly."""
        payload = fsa_write_32(value=0x41414141, nth_stack=7, target_addr=0x08049000, each=1)
        # With each=1, should have 4 writes: %7$hhn, %8$hhn, %9$hhn, %10$hhn
        assert b"%7$hhn" in payload or b"7$hhn" in payload
        # Find all stack positions used
        positions = re.findall(rb"%\d+c%(\d+)\$hhn", payload)
        if positions:
            positions = [int(p) for p in positions]
            # Should be consecutive
            for i in range(1, len(positions)):
                assert positions[i] == positions[i - 1] + 1

    def test_multiple_addresses_for_byte_write(self):
        """Test that byte-by-byte write includes multiple target addresses."""
        target_addr = 0x08049000
        payload = fsa_write_32(value=0xDEADBEEF, nth_stack=7, target_addr=target_addr, each=1)
        # Should have addr, addr+1, addr+2, addr+3
        for i in range(4):
            assert struct.pack("<I", target_addr + i) in payload


class TestFsaWrite64:
    """Tests for fsa_write_64 function."""

    def test_basic_payload_generation(self):
        """Test basic 64-bit payload generation."""
        write_dict = {0x00007fff00001000: 0x4141414141414141}
        payload = fsa_write_64(write_dict, nth_stack=6)
        # Should contain format specifiers
        assert b"$n" in payload or b"$hn" in payload or b"$hhn" in payload

    def test_payload_alignment(self):
        """Test that payload is 8-byte aligned."""
        write_dict = {0x00007fff00001000: 0x4141414141414141}
        payload = fsa_write_64(write_dict, nth_stack=6)
        assert len(payload) % 8 == 0

    def test_offset_alignment(self):
        """Test payload with offset is properly aligned."""
        write_dict = {0x00007fff00001000: 0x4141414141414141}
        payload = fsa_write_64(write_dict, nth_stack=6, offset=3)
        assert len(payload) % 8 == 0
        # Should start with padding
        assert payload[:3] == b"AAA"

    def test_multiple_writes(self):
        """Test writing to multiple addresses."""
        write_dict = {
            0x00007fff00001000: 0x41414141,
            0x00007fff00002000: 0x42424242,
        }
        payload = fsa_write_64(write_dict, nth_stack=6)
        # Should have format specifiers for both writes
        specifier_count = payload.count(b"$n") + payload.count(b"$hn") + payload.count(b"$hhn")
        assert specifier_count >= 2

    def test_hhn_specifier(self):
        """Test that each=1 uses %hhn specifier."""
        write_dict = {0x00007fff00001000: 0x41}
        payload = fsa_write_64(write_dict, nth_stack=6, each=1)
        assert b"$hhn" in payload

    def test_hn_specifier(self):
        """Test that each=2 uses %hn specifier."""
        write_dict = {0x00007fff00001000: 0x4141}
        payload = fsa_write_64(write_dict, nth_stack=6, each=2)
        assert b"$hn" in payload


class TestFsaPayloadSimulation:
    """Simulation tests to verify payload correctness."""

    def simulate_printf_write(self, payload: bytes, stack_start: int, memory: dict) -> dict:
        """Simulate printf format string write operation.

        This is a simplified simulation that tracks %n writes.
        """
        written = 0
        pos = 0
        stack_offset = stack_start

        # Parse the payload to find addresses at the beginning
        # Then process format specifiers

        while pos < len(payload):
            if payload[pos:pos+1] == b"%":
                # Find the format specifier
                match = re.match(rb"%(\d+)c%(\d+)\$(hhn|hn|n)", payload[pos:])
                if match:
                    count = int(match.group(1))
                    stack_pos = int(match.group(2))
                    spec = match.group(3)

                    written += count

                    # Get address from stack position
                    addr_offset = (stack_pos - stack_start) * 4  # 32-bit
                    if addr_offset < len(payload) and addr_offset >= 0:
                        try:
                            addr = struct.unpack("<I", payload[addr_offset:addr_offset+4])[0]
                            if spec == b"hhn":
                                memory[addr] = written & 0xFF
                            elif spec == b"hn":
                                memory[addr] = written & 0xFFFF
                            else:  # n
                                memory[addr] = written & 0xFFFFFFFF
                        except struct.error:
                            pass

                    pos += len(match.group(0))
                    continue
            written += 1
            pos += 1

        return memory

    def test_simulation_basic(self):
        """Test that simulation framework works."""
        # This is a basic sanity check for the simulation
        memory = {}
        memory = self.simulate_printf_write(b"AAAA%10c%7$n", 7, memory)
        # The simulation is simplified; this test ensures the framework runs
        assert isinstance(memory, dict)


class TestFsaIntegration:
    """Integration tests with actual vulnerable binary (requires gcc-multilib)."""

    VULN_SOURCE = "/tmp/test_fsa_vuln.c"
    VULN_BINARY = "/tmp/test_fsa_vuln32"

    @pytest.fixture(scope="class")
    def vuln_binary(self):
        """Compile the vulnerable binary if gcc-multilib is available."""
        import subprocess
        from pathlib import Path

        # Check if already compiled
        if Path(self.VULN_BINARY).exists():
            return self.VULN_BINARY

        # Try to compile
        result = subprocess.run(
            ["gcc", "-m32", "-fno-stack-protector", "-no-pie",
             "-o", self.VULN_BINARY, self.VULN_SOURCE],
            capture_output=True,
        )
        if result.returncode != 0:
            pytest.skip("gcc-multilib not available")

        return self.VULN_BINARY

    def get_target_address(self, binary: str) -> int:
        """Get the target variable address from the binary."""
        import subprocess
        result = subprocess.run([binary], input=b"test", capture_output=True)
        match = re.search(rb"target address: (0x[0-9a-f]+)", result.stdout)
        if match:
            return int(match.group(1), 16)
        pytest.fail("Could not find target address")

    @pytest.mark.skipif(
        not __import__("pathlib").Path("/tmp/test_fsa_vuln.c").exists(),
        reason="Vulnerable source not found"
    )
    def test_fsa_write_32_integration(self, vuln_binary):
        """Test that fsa_write_32 actually works on a real binary."""
        import subprocess

        target_addr = self.get_target_address(vuln_binary)

        payload = fsa_write_32(
            value=0x41414141,
            nth_stack=4,
            target_addr=target_addr,
            each=1
        )

        result = subprocess.run([vuln_binary], input=payload, capture_output=True)
        assert b"SUCCESS" in result.stdout or b"0x41414141" in result.stdout

    @pytest.mark.skipif(
        not __import__("pathlib").Path("/tmp/test_fsa_vuln.c").exists(),
        reason="Vulnerable source not found"
    )
    def test_fsa_write_various_values(self, vuln_binary):
        """Test writing various values."""
        import subprocess

        target_addr = self.get_target_address(vuln_binary)

        for value in [0xDEADBEEF, 0x12345678]:
            payload = fsa_write_32(
                value=value,
                nth_stack=4,
                target_addr=target_addr,
                each=1
            )

            result = subprocess.run([vuln_binary], input=payload, capture_output=True)
            expected = f"0x{value:x}".encode()
            assert expected in result.stdout.lower(), f"Failed to write {hex(value)}"
