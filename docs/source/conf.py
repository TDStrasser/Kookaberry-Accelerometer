# Configuration file for the Sphinx documentation builder.
from datetime import datetime

# -- Project information

project = 'KookaBlockly Template'
now = datetime.now()
today = f"{now.year}-{now.month:02}-{now.day:02}"

rights_holders = 'the AustSTEM Foundation and contributors'
copyright = f"2019-{now.year} {rights_holders}. Last updated: {today}"

author = 'Julian Dinsdale and Tony Strasser'

release = '0.1'
version = '0.1.0'

numfig = True # Automatically number figures, code blocks and tables

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
