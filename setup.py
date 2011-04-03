#!/usr/bin/env python

from distutils.core import setup
import glob, os, re

includes = []
#includes_target = 'share/skel/'
includes_target = 'share/fiat/'
includes_dir = 'share'

for root, dirs, filenames in os.walk(includes_dir):
    if root is includes_dir:
        final = includes_target
    else:
        final = includes_target + root[len(includes_dir)+1:] + '/'
    files = []
    
    if not re.search(r'.svn', root):
        for file in filenames:
            if (file[0] != '.'):
                files.append(os.path.join(root, file))
        includes.append((final, files))

setup(name='xenadu',
      version='0.1',
      description='Xenadu manages system configurations',
      author='Ian Dennis Miller',
      author_email='ian@saperea.com',
      url=' http://code.google.com/p/xenadu/',
      packages=['Xenadu', 'Xenadu.Task'],
      package_dir = {'': 'lib'},
      long_description="Xenadu manages system configurations",
      scripts=['bin/xenadu'],
      data_files = includes,
      license="GPL v2",
      platforms=["any"],
     )

