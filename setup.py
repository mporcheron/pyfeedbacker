# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pyfeedbacker',
    version='0.1.0',
    description='Python CLI application for generating feedback on student assignments',
    long_description=readme,
    author='Martin Porcheron',
    author_email='matin+pyfeedbacker@porcheron.uk',
    url='hhttps://github.com/mporcheron/pyfeedbacker',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)