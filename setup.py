from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.6'
DESCRIPTION = 'GSP Python implementation'
LONG_DESCRIPTION = 'A Python implementation of Generalized Sequential Patterns (GSP) algorithm for sequential pattern mining'

# Setting up
setup(
    name="gsp-python",
    version=VERSION,
    author="Slocon",
    author_email="<79758160+Slocon00@users.noreply.github.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'gsp', 'data mining', 'sequential pattern mining', 'seuence mining'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    project_urls={
        'Source': "https://github.com/Slocon00/GSP-python",
    },
)
