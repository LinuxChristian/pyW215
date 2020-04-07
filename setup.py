# -*- coding: utf-8 -*-
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pyW215',
      version='0.7.0',
      description='Interface for d-link W215 Smart Plugs.',
      long_description=long_description,
      url='https://github.com/linuxchristian/pyW215',
      author='Christian Juncker Brædstrup',
      author_email='christian@junckerbraedstrup.dk',
      license='MIT',
      keywords='D-Link W215 W110 Smartplug',
      packages=['pyW215'],
      install_requires=[],
      zip_safe=False)
