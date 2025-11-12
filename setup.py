#!./venv/bin/python3
'''
Created on 20220926
Update on 20251111
@author: Eduardo Pagotto
'''

import os
import codecs
from setuptools import setup, find_packages

from zencomm import __version__ as VERSION

PACKAGE = "zencomm"

# listar os packages
#python -c "from setuptools import setup, find_packages; print(find_packages())"

# Classifiers
# https://pypi.org/classifiers/

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="zencomm",
    version=VERSION,
    author="Eduardo Pagotto",
    author_email="edupagotto@gmail.com",
    description="Socket/Unix communication Python classes",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/EduardoPagotto/zencomm.git",
    packages=find_packages(
        where=".",
        exclude=["tests.*", "tests"]
    ),
    platforms='any',
    include_package_data=True,
    license=read('LICENSE'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires=['setuptools',
                      'typing_extensions',
                      'wheel',
                      'aiologger'])
