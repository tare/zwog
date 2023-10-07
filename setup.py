#!/usr/bin/env python
"""Zwift workout generator (zwog)."""
import os

from setuptools import setup

# read the long description
with open(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md"),
    encoding="utf-8",
) as f:
    long_description = f.read()

setup(
    name="zwog",
    version="0.0.2",
    description="Zwift workout generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tarmo Äijö",
    url="https://github.com/tare/zwog",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    packages=["zwog"],
    install_requires=["lark~=1.1.2"],
    scripts=["bin/zwog"],
)
