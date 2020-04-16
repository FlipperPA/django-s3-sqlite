# django-s3-sqlite

[![PyPI](https://img.shields.io/pypi/v/django-s3-sqlite.svg)](https://pypi.python.org/pypi/django-s3-sqlite)

This project was inspired and started with [Zappa](https://github.com/Miserlou/Zappa). Thanks to [Rich Jones](https://github.com/Miserlou) for all of his amazing work.

## Installation

Install via `pip`:
    
    $ pip install django-s3-sqlite

Add to your installed apps:

    INSTALLED_APPS += ["django_s3_sqlite"]

## Using an S3-Backed Database Engine

`django-s3-sqlite` allows use of an [S3-synced SQLite database](https://blog.zappa.io/posts/s3sqlite-a-serverless-relational-database) as a Django database engine.

This will cause problems for applications with concurrent writes**, but it scales very well for high-read applications that don't have concurrent writes (like a CMS for your blog), and it's orders of magnitude cheaper than AWS RDS or Aurora (pennies per month instead of many dollars per month).

** Concurrent writes will often be lost and not show up in concurrent readers. This is because the database is transferred between S3 storage and the Lambda instance for each request.

#### Django Settings & Commands

```python
DATABASES = {
    "default": {
        "ENGINE": "django_s3_sqlite",
        "NAME": "sqlite.db",
        "BUCKET": "your-db-bucket",
    }
}
```

Newer versions of Django (v2.1+) require a newer version of SQLite (3.8.3+) than is available on AWS Lambda instances (3.7.17).

**Because of this, you will need to download the provided `_sqlite3.so` for your Python version (available in the `shared-objects` directory of this repository) and put it at the root of your Django project.** These shared object files contain a compiled binary static build of SQLite 3.30.1 that can be used with the corresponding version of Python. We hope this will soon be available via [Lambda Packages](https://github.com/Miserlou/lambda-packages), but for now, you will also need to add this line to your Zappa JSON settings file in each environment:

```
"use_precompiled_packages": false,
```

Since SQLite keeps the database in a single file, you will want to keep it as small and defragmented as possible. It is good to occasionally perform a database vacuum, especially after deleting or updating data. There's a command to vacuum your database:

```bash
zappa manage [instance] s3_sqlite_vacuum
```

## Running manage.py commands

To update your database, you **must** do so via Zappa, via the below example:

    $ zappa manage <stage> migrate


You'll probably need a default user to manage your application with, so you can now:

    $ zappa manage <stage> create_admin_user

Or you can pass some arguments:
   
    $ zappa manage <stage> create_admin_user one two three

This will internally make this call:

```python
User.objects.create_superuser('one', 'two', 'three')
```

## Release Notes

On GitHub: https://github.com/FlipperPA/django-s3-sqlite/releases

## Maintainers and Creator

* Maintainer: Tim Allen (https://github.com/FlipperPA/)
* Maintainer: Peter Baumgartner (https://github.com/ipmb/)
* Original Creator: Rich Jones (https://github.com/Miserlou/)

This package is largely maintained by the staff of [Wharton Research Data Services](https://wrds.wharton.upenn.edu/). We are thrilled that [The Wharton School](https://www.wharton.upenn.edu/) allows us a certain amount of time to contribute to open-source projects. We add features as they are necessary for our projects, and try to keep up with Issues and Pull Requests as best we can. Due to time constraints (our full time jobs!), Feature Requests without a Pull Request may not be implemented, but we are always open to new ideas and grateful for contributions and our package users.

### Contributors - Thank You!

* Viktor Chaptsev (https://github.com/vchaptsev/)
* Almog Cohen (https://github.com/AlmogCohen/)
* Lucas Connors (https://github.com/RevolutionTech)
* Paul Bailey (https://github.com/pizzapanther/)
* Noorhteen Raja J (https://github.com/jnoortheen/)
* jjorissen52 (https://github.com/jjorissen52/)
* James Winegar (https://github.com/jameswinegar/)
* Edgar Roman (https://github.com/edgarroman/)

### Build Instructions for _sqlite3.so

If you'd like to use a different version of Python or SQLite than what is provided in this repo, you will need to build the static binary yourself. These instructions show you how to build the file: https://charlesleifer.com/blog/compiling-sqlite-for-use-with-python-applications/

After you've downloaded SQLite, follow the instructions to install it into a virtual environment. You must perform the installation on Amazon Linux or CentOS 7 (which Amazon Linux is based on).
