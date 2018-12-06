#!/usr/bin/env python
import io
from setuptools import setup, find_packages

with io.open('./README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="PyCovenantSQL",
    version="0.1.0",
    url='https://github.com/CovenantSQL/python-driver/',
    project_urls={
        "Documentation": "https://pycovenantsql.readthedocs.io/",
    },
    description='Pure Python CovenantSQL Driver',
    long_description=readme,
    packages=find_packages(exclude=['tests*', 'pycovenantsql.tests*']),
    install_requires=[
        "requests",
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Topic :: Database',
    ],
    keywords=("CovenantSQL","driver","database"),

    author = "laodouya",
    author_email = "jin.xu@CovenantSQL.io",
    license = "Apache 2.0 Licence",
)

