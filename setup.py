#!/usr/bin/env python
from setuptools import setup, find_packages
 
setup(
    name='toyotama',
    version='0.5',
    description='CTF lib',
    py_modules=['toyotama'],
    author='Laika',
    python_requires='>=3.6.*, <4',
    install_requires=['gmpy2']
)




