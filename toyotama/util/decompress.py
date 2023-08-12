import argparse
import bz2
import tarfile
from pathlib import Path
from zipfile import ZipFile

import py7zr


def parse_args():
    parser = argparse.ArgumentParser(description="Decompress a file")
    parser.add_argument("input", type=str, help="Compressed file")
    return parser.parse_args()


def decompress_zip(input_file: Path, output_file: Path):
    with ZipFile(input_file, "r") as zip_file:
        zip_file.extractall(output_file)


def decompress_bz2(input_file: Path, output_file: Path):
    with bz2.open(input_file, "rb") as bz2_file:
        with open(output_file, "wb") as output:
            for data in iter(lambda: bz2_file.read(100 * 1024), b""):
                output.write(data)


def decompress_7z(input_file: Path, output_file: Path):
    with py7zr.SevenZipFile(input_file, "r") as archive:
        archive.extractall(output_file)


def decompress_tar(input_file: Path, output_file: Path):
    with tarfile.open(input_file, "r") as archive:
        archive.extractall(output_file)


def get_file_format(file_path: Path):
    # Define magic number signatures for different formats
    magic_numbers = {
        b"\x50\x4B\x03\x04": "Zip",
        b"\x37\x7A\xBC\xAF\x27\x1C": "7z",
        b"\x1F\x8B\x08": "Gzip",
        b"\x42\x5A\x68": "Bzip2",
        b"\xFD\x37\x7A\x58\x5A\x00": "XZ",
    }

    with open(file_path, "rb") as file:
        signature = file.read(6)  # Read the first 6 bytes

    for magic, format_name in magic_numbers.items():
        if signature.startswith(magic):
            return format_name

    return "Unknown"


def decompress(args):
    input_path = Path(args.input)
    match get_file_format(input_path):
        case "Zip":
            decompress_zip(input_path, input_path.parent)
        case "Bzip2":
            decompress_bz2(input_path, input_path.parent)
        case "7z":
            decompress_7z(input_path, input_path.parent)
        case "Gzip":
            decompress_tar(input_path, input_path.parent)
        case "XZ":
            decompress_tar(input_path, input_path.parent)
        case _:
            print("Unknown file format")


def main():
    args = parse_args()
    decompress(args)
