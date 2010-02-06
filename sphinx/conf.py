# -*- coding: utf-8 -*-
#

import sys, os
sys.path.append('/Users/idm/Code/google_code/xenadu/lib')

# -- General configuration -----------------------------------------------------
extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'Xenadu'
copyright = u'2010, Ian Dennis Miller'
version = '0.9'
release = '0.9'

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------
html_theme = 'default'
html_static_path = ['_static']
# Output file base name for HTML help builder.
htmlhelp_basename = 'xenadudoc'

# -- Options for LaTeX output --------------------------------------------------
# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'xenadu.tex', u'Xenadu Documentation',
   u'Ian Dennis Miller', 'manual'),
]
