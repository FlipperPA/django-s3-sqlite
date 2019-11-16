import os
import sys
from setuptools import setup
from io import open

# New PyPI handles markdown! Yay!
with open('README.md') as f:
    README = f.read()

setup(
    name='django-s3sqlite',
    version='0.0.1',
    packages=['django_s3sqlite'],
    install_requires=required,
    include_package_data=True,
    license='BSD License',
    description='Helpers for Django Zappa deployments',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Miserlou/zappa-django-utils',
    author='Rich Jones',
    author_email='rich@openwatch.net',
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
