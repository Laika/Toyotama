#!/usr/bin/env python
from setuptools import setup, find_packages
 
setup(
    name='toyotama',
    version='0.6',
    description='CTF libary',
    py_modules=['toyotama','log'],
    author='Laika',
    python_requires='>=3.6.*, <4',
    install_requires=['gmpy2']
)




