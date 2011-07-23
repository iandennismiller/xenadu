#!/usr/bin/env python

from distutils.core import setup
import glob, os, re

setup(name='xenadu',
      version='0.2',
      description='Xenadu manages system configurations',
      author='Ian Dennis Miller',
      author_email='ian@iandennismiller.com',
      url=' http://github.com/iandennismiller/xenadu/',
      packages=['Xenadu', 'Xenadu.Task'],
      package_dir = {'': 'lib'},
      long_description="Xenadu manages system configurations, making them easy to track with version control software",
      license="GPL v2",
      scripts=['bin/xenadu'],
      platforms=["any"],
     )

