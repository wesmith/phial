#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='phial',
    version='0.1.1',
    author='Steve Pothier',
    url='http://github.com/pothiers/phial',
    description='A container for tools that support running Phi experiments',
    long_description=readme,
    license='GNU General Public License v3.0',
    install_requires=[
        'pyphi>=1.1.0',
        'networkx>2.0.0'],
    packages=['phial'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ]
)
