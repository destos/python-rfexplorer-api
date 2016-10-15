#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click==6.0',
    'pyserial==3.1.1',
    'python_measurement==1.8.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='python_rfexplorer_api',
    version='0.1.0',
    description="Python API for the RFExplorer Device",
    long_description=readme + '\n\n' + history,
    author="Patrick Forringer",
    author_email='patrick@forringer.com',
    url='https://github.com/destos/python_rfexplorer_api',
    packages=[
        'python_rfexplorer_api',
    ],
    package_dir={'python_rfexplorer_api':
                 'python_rfexplorer_api'},
    entry_points={
        'console_scripts': [
            'python_rfexplorer_api=python_rfexplorer_api.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='python_rfexplorer_api',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
