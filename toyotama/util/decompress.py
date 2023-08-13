import argparse
import bz2
import os
import tarfile
from pathlib import Path
from zipfile import ZipFile

import py7zr

from toyotama.util.log import get_logger

logger = get_logger(__name__, "DEBUG")


def parse_args():
    parser = argparse.ArgumentParser(description="Decompress a file")
    parser.add_argument("input", type=str, help="Compressed file")
    parser.add_argument("-k", "--keep", action="store_true", help="Keep the compressed file")
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
            logger.info("Zip file detected")
            decompress_zip(input_path, input_path.parent)
        case "Bzip2":
            logger.info("Bzip2 file detected")
            decompress_bz2(input_path, input_path.parent)
        case "7z":
            logger.info("7z file detected")
            decompress_7z(input_path, input_path.parent)
        case "Gzip":
            logger.info("Gzip file detected")
            decompress_tar(input_path, input_path.parent)
        case "XZ":
            logger.info("XZ file detected")
            decompress_tar(input_path, input_path.parent)
        case _:
            logger.error("Unknown file format")
            raise ValueError("Unknown file format")

    if not args.keep:
        logger.debug("Removing %s", args.input)
        os.remove(input_path)


def main():
    args = parse_args()
    decompress(args)
