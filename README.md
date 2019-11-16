# django-s3-sqlite

[![PyPI](https://img.shields.io/pypi/v/zappa-django-utils.svg)](https://pypi.python.org/pypi/django-s3-sqlite)

This project was inspired and started for [Zappa](https://github.com/Miserlou/Zappa). Thanks to [Rich Jones](https://github.com/Miserlou) for all of his amazing work.

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
    'default': {
        'ENGINE': 'django_s3_sqlite.db',
        'NAME': 'sqlite.db',
        'BUCKET': 'your-db-bucket'
    }
}
```

And... that's it! Since SQLite keeps the database in a single file, you will want to keep it as small and defragmented as possible. It is good to occasionally perform a database vacuum, especially after deleting or updating data. There's a command to vacuum your database:

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
