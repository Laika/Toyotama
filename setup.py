#!/usr/bin/env python
from setuptools import setup, find_packages
 
setup(
    name='toyotama',
    version='0.7',
    description='CTF libary',
    py_modules=['toyotama','log', 'integer'],
    author='Laika',
    python_requires='>=3.8.*, <4',
    install_requires=['gmpy2', 'requests']
)




