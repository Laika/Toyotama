#!/usr/bin/env python
from setuptools import find_packages, setup


def _requires_from_file(filename):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="toyotama",
    version="0.9.3",
    description="CTF libary",
    packages=find_packages(),
    py_modules=["toyotama", "log", "integer"],
    author="Laika",
    author_email="laika@albina.cc",
    python_requires=">=3.9.*, <4",
    install_requires=_requires_from_file("requirements.txt"),
)
