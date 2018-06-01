# zappa-django-utils

[![PyPI](https://img.shields.io/pypi/v/zappa-django-utils.svg)](https://pypi.python.org/pypi/zappa-django-utils)
[![Slack](https://img.shields.io/badge/chat-slack-ff69b4.svg)](https://slack.zappa.io/)
[![Gun.io](https://img.shields.io/badge/made%20by-gun.io-blue.svg)](https://gun.io/)
[![Patreon](https://img.shields.io/badge/support-patreon-brightgreen.svg)](https://patreon.com/zappa)


Small utilities for making [Zappa](https://github.com/Miserlou/Zappa) deployments slightly easier for Django applications.

This project was inspired by Edgar Roman's [Zappa Django Guide](https://github.com/edgarroman/zappa-django-guide).

## Installation

Install via `pip`:
    
    $ pip install zappa-django-utils

Add to your installed apps:

    INSTALLED_APPS += ('zappa_django_utils',)

## Usage

### Using an S3-Backed Database Engine

**ZDU** includes the ability to use `s3sqlite`, an [S3-synced SQLite database](https://blog.zappa.io/posts/s3sqlite-a-serverless-relational-database) as a Django database engine.

This will cause problems for applications with concurrent writes**, but it scales very well for high-read applications that don't have concurrent writes (like CMSes), and it's orders of magnitude cheaper than AWS RDS.

** Concurrent writes will often be lost and not show up in concurrent readers. This is because the database is transferred between S3 storage and the Lambda instance for each request.

#### Django Settings & Commands

```python
DATABASES = {
    'default': {
        'ENGINE': 'zappa_django_utils.db.backends.s3sqlite',
        'NAME': 'sqlite.db',
        'BUCKET': 'your-db-bucket'
    }
}
```

And... that's it! Since SQLite keeps the database in a single file, you will want to keep it as small and defragmented as possible. It is good to occasionally perform a database vacuum, especially after deleting or updating data. There's a command to vacuum your database:

```bash
zappa manage [instance] s3sqlite_vacuum
```

### Creating a Postgres Database

Once you have your RDS set up, your VPC/Subnet/Security Groups set up, and your `DATABASES` setting set up, you can create the database with:

    $ zappa manage <stage> create_pg_db

Then you're ready to `python manage.py makemigrations` and `zappa update; zappa manage migrate`!

### Creating a Default Admin User 

You'll probably need a default user to manage your application with, so you can now:

    $ zappa manage <stage> create_admin_user

Or you can pass some arguments:
   
    $ zappa manage <stage> create_admin_user one two three

This will internally make this call:

```python
User.objects.create_superuser('one', 'two', 'three')
```

Now log in and immediately change the admin user's email and password.

### Creating/Dropping a Postgres Schema

You can create a [Postgres schema](https://www.postgresql.org/docs/current/static/ddl-schemas.html) with:

    $ zappa manage create_pg_schema

and drop it with:

    $ zappa manage drop_pg_schema

## License

(c) 2017, Rich Jones, MIT License
