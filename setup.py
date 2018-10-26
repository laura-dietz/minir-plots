#!/usr/bin/env python3
from setuptools import setup

setup(
    name='minir-plots',
    version='1.1',
    packages=[],
    py_modules=["column", "pairedttest", "column_difficulty", "hurtshelps", "feature_column"],
    
    url='minir-plots.cs.unh.edu',
    license='BSD 3-Clause',
    author='laura-dietz',
    author_email='Laura.Dietz@unh.edu',
    description='plotting trec_eval results',
    install_requires=['pandas'],
    dependency_links=['git+https://github.com/laura-dietz/minir-plots.git'],


    entry_points={
        'console_scripts': [
            'minir-column=column:main',
            'minir-pairttest=pairedttest:main',
            'minir-column-difficulty=column_difficulty:main',
            'minir-feature-column=feature_column:main',
            'minir-hurtshelps=hurtshelps:main'
        ],
    }    
)
