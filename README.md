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

Because of this, you will need to download the file `_sqlite3.so` (available in the root of this repository) and put it at the root of your Django project. The file contains a compiled binary static build of SQLite 3.30.1 for Python 3.6. We hope this will soon be included on [Lambda Packages](https://github.com/Miserlou/lambda-packages), but for now, you will also need to add this line to your Zappa JSON settings file in each environment:

```
"use_precompiled_packages": false,
```

Since SQLite keeps the database in a single file, you will want to keep it as small and defragmented as possible. It is good to occasionally perform a database vacuum, especially after deleting or updating data. There's a command to vacuum your database:

```bash
zappa manage [instance] s3_sqlite_vacuum
```

## Creating a Default Admin User 

You'll probably need a default user to manage your application with, so you can now:

    $ zappa manage <stage> create_admin_user

Or you can pass some arguments:
   
    $ zappa manage <stage> create_admin_user one two three

This will internally make this call:

```python
User.objects.create_superuser('one', 'two', 'three')
```

## Creator and Maintainer

* Creator: Rich Jones (https://github.com/Miserlou/)
* Maintainer: Tim Allen (https://github.com/FlipperPA/)

This package is largely maintained by the staff of [Wharton Research Data Services](https://wrds.wharton.upenn.edu/). We are thrilled that [The Wharton School](https://www.wharton.upenn.edu/) allows us a certain amount of time to contribute to open-source projects. We add features as they are necessary for our projects, and try to keep up with Issues and Pull Requests as best we can. Due to time constraints (our full time jobs!), Feature Requests without a Pull Request may not be implemented, but we are always open to new ideas and grateful for contributions and our package users.

### Contributors - Thank You!

* Viktor Chaptsev (https://github.com/vchaptsev/)
* Almog Cohen (https://github.com/AlmogCohen/)
* Paul Bailey (https://github.com/pizzapanther/)
* Noorhteen Raja J (https://github.com/jnoortheen/)
* jjorissen52 (https://github.com/jjorissen52/)
* James Winegar (https://github.com/jameswinegar/)
* Edgar Roman (https://github.com/edgarroman/)

### Build Instructions for _sqlite3.so

These instructions show how to build the static binary necessary: https://charlesleifer.com/blog/compiling-sqlite-for-use-with-python-applications/

It must be done on Amazon Linux or CentOS 7 (which Amazon Linux is based on).
