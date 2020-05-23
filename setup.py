#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from setuptools import setup


setup(
    name="delta_crdt",
    version="0.0.0",
    license="MIT",
    description="A Python implementation of Delta CRDTs",
    long_description="",
    author="Richard Tibbles",
    author_email="richard@learningequality.org",
    url="https://github.com/rtibbles/delta-crdt",
    packages=["delta_crdt"],
    package_dir={"delta_crdt": "src/python_delta_crdt"},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    project_urls={
        "Changelog": "https://github.com/rtibbles/delta-crdt/blob/master/CHANGELOG.rst",
        "Issue Tracker": "https://github.com/rtibbles/delta-crdt/issues",
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=["msgpack==1.0.0", "six==1.14.0"],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
)
