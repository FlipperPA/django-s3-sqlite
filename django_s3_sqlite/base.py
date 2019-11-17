from django.db.backends.sqlite3.base import DatabaseWrapper

from hashlib import md5
from io import BytesIO
from logging import debug as logging_debug
from os import path

import boto3
import botocore


class DatabaseWrapper(DatabaseWrapper):
    """
    Wraps the normal Django SQLite DB engine in one that shuttles the SQLite database
    back and forth from an S3 bucket.
    """

    def load_remote_db(self):
        """
        Load the database from the S3 storage bucket into the current AWS Lambda
        instance.
        """
        signature_version = self.settings_dict.get("SIGNATURE_VERSION", "s3v4")
        s3 = boto3.resource(
            's3',
            config=botocore.client.Config(signature_version=signature_version),
        )

        if '/tmp/' not in self.settings_dict['NAME']:
            try:
                etag = ''
                if path.isfile('/tmp/' + self.settings_dict['NAME']):
                    m = md5()
                    with open('/tmp/' + self.settings_dict['NAME'], 'rb') as f:
                        m.update(f.read())

                    # In general the ETag is the md5 of the file, in some cases it's
                    # not, and in that case we will just need to reload the file,
                    # I don't see any other way
                    etag = m.hexdigest()

                obj = s3.Object(
                    self.settings_dict['BUCKET'],
                    self.settings_dict['NAME'],
                )
                obj_bytes = obj.get(
                    IfNoneMatch=etag,
                )["Body"]  # Will throw E on 304 or 404

                with open('/tmp/' + self.settings_dict['NAME'], 'wb') as f:
                    f.write(obj_bytes.read())

                m = md5()
                with open('/tmp/' + self.settings_dict['NAME'], 'rb') as f:
                    m.update(f.read())

                self.db_hash = m.hexdigest()

            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "304":
                    logging_debug(
                        "ETag matches md5 of local copy, using local copy of DB!",
                    )
                    self.db_hash = etag
                else:
                    logging_debug("Couldn't load remote DB object.")
            except Exception as e:
                # Weird one
                logging_debug(e)

        # SQLite DatabaseWrapper will treat our tmp as normal now
        # Check because Django likes to call this function a lot more than it should
        if '/tmp/' not in self.settings_dict['NAME']:
            self.settings_dict['REMOTE_NAME'] = self.settings_dict['NAME']
            self.settings_dict['NAME'] = '/tmp/' + self.settings_dict['NAME']

        # Make sure it exists if it doesn't yet
        if not path.isfile(self.settings_dict['NAME']):
            open(self.settings_dict['NAME'], 'a').close()

        logging_debug("Loaded remote DB!")

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.db_hash = None
        self.load_remote_db()

    def close(self, *args, **kwargs):
        """
        Engine closed, copy file to DB if it has changed
        """
        super(DatabaseWrapper, self).close(*args, **kwargs)

        signature_version = self.settings_dict.get("SIGNATURE_VERSION", "s3v4")
        s3 = boto3.resource(
            's3',
            config=botocore.client.Config(signature_version=signature_version),
        )

        try:
            with open(self.settings_dict['NAME'], 'rb') as f:
                fb = f.read()

                m = md5()
                m.update(fb)
                if self.db_hash == m.hexdigest():
                    logging_debug("Database unchanged, not saving to remote DB!")
                    return

                bytesIO = BytesIO()
                bytesIO.write(fb)
                bytesIO.seek(0)

                s3_object = s3.Object(
                    self.settings_dict['BUCKET'],
                    self.settings_dict['REMOTE_NAME'],
                )
                s3_object.put('rb', Body=bytesIO)
        except Exception as e:
            logging_debug(e)

        logging_debug("Saved to remote DB!")
