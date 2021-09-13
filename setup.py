#!/usr/bin/env python
import sys
from setuptools import find_packages, setup

if sys.version_info[:2] < (3, 8):
    raise RuntimeError("Python version >= 3.9 required.")


def _requires_from_file(filename):
    with open(filename) as f:
        return f.read().splitlines()


metadata = dict(
    name="Toyotama",
    version="0.9.4",
    description="CTF library",
    packages=find_packages(),
    py_modules=["toyotama", "log", "integer"],
    author="Laika",
    author_email="laika@albina.cc",
    maintainer="Laika",
    maintainer_email="laika@albina.cc",
    python_requires=">=3.9.*, <4",
    install_requires=_requires_from_file("requirements.txt"),
    download_url="https://pypi.org/project/toyotama",
    project_urls={
        "Source Code": "https://github.com/Laika/Toyotama",
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
    ],
)

setup(**metadata)
