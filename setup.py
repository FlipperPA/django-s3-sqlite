from setuptools import setup, find_packages
from io import open

with open("README.md") as f:
    README = f.read()

setup(
    name="django-s3-sqlite",
    packages=find_packages(),
    install_requires=["Django>=2"],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    include_package_data=True,
    license="BSD License",
    description="An AWS S3-hosted SQLite database backend for Django.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/FlipperPA/django-s3-sqlite/",
    author="Timothy Allen",
    author_email="flipper@peregrinesalon.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
