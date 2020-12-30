#!/usr/bin/env python
from setuptools import find_packages, setup


def _requires_from_file(filename):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="toyotama",
    version="0.9",
    description="CTF libary",
    packages=find_packages(),
    py_modules=["toyotama", "log", "integer"],
    author="Laika",
    python_requires=">=3.8.*, <4",
    install_requires=_requires_from_file("requirements.txt"),
)
