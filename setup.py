#!/usr/bin/env python

from io import open
import os
from setuptools import setup


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


setup(
    name="speckenv",
    version="1.2",
    description="",
    long_description=read("README.rst"),
    author="Matthias Kestenholz",
    author_email="mk@feinheit.ch",
    url="https://github.com/matthiask/speckenv/",
    license="BSD License",
    platforms=["OS Independent"],
    py_modules=["speckenv"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    test_suite="test_speckenv",
    zip_safe=False,
)
