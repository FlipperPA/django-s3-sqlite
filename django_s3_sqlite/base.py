import base64
import binascii
import logging
from hashlib import md5
from os import path

import boto3
import botocore
from django.db.backends.sqlite3.base import DatabaseWrapper

log = logging.getLogger(__name__)


def _get_md5(file_bytes: bytes) -> str:
    """Given bytes, calculate their md5 hash"""
    m = md5()
    m.update(file_bytes)
    return m.hexdigest()


def _get_bytes(filename: str) -> bytes:
    """Read file as bytes"""
    with open(filename, "rb") as f:
        return f.read()


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

        if "/tmp/" not in self.settings_dict["NAME"]:
            local_file_path = "/tmp/" + self.settings_dict["NAME"]
            if path.isfile(local_file_path):
                current_md5 = _get_md5(_get_bytes(local_file_path))
            else:
                current_md5 = ""
            try:
                # In general the ETag is the md5 of the file, in some cases it's
                # not, and in that case we will just need to reload the file,
                # I don't see any other way
                obj_bytes = self.s3.Object(
                    self.settings_dict["BUCKET"], self.settings_dict["NAME"],
                ).get(IfNoneMatch=current_md5,)[
                    "Body"
                ]  # Will throw E on 304 or 404

                # Remote does not match local. Replace local copy.
                with open(local_file_path, "wb") as f:
                    file_bytes = obj_bytes.read()
                    self.db_hash = _get_md5(file_bytes)
                    f.write(file_bytes)
                    log.debug("Database downloaded from S3.")

            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "304":
                    log.debug(
                        "ETag matches md5 of local copy, using local copy of DB!",
                    )
                    self.db_hash = current_md5
                else:
                    log.exception("Couldn't load remote DB object.")
            except Exception as e:
                # Weird one
                log.exception("An unexpected error occurred.")

        # SQLite DatabaseWrapper will treat our tmp as normal now
        # Check because Django likes to call this function a lot more than it should
        if "/tmp/" not in self.settings_dict["NAME"]:
            self.settings_dict["REMOTE_NAME"] = self.settings_dict["NAME"]
            self.settings_dict["NAME"] = "/tmp/" + self.settings_dict["NAME"]

        # Make sure it exists if it doesn't yet
        if not path.isfile(self.settings_dict["NAME"]):
            open(self.settings_dict["NAME"], "a").close()

        if self.db_hash is None:
            self.db_hash = _get_md5(_get_bytes(self.settings_dict["NAME"]))
        log.debug("Local database is ready. md5:%s", self.db_hash)

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        signature_version = self.settings_dict.get("SIGNATURE_VERSION", "s3v4")
        aws_s3_access_key = self.settings_dict.get("AWS_S3_ACCESS_KEY", None)
        aws_s3_access_secret = self.settings_dict.get("AWS_S3_ACCESS_SECRET", None)
        if aws_s3_access_key and aws_s3_access_secret:
            session = boto3.Session(
                aws_access_key_id=aws_s3_access_key,
                aws_secret_access_key=aws_s3_access_secret,
            )
            self.s3 = session.resource(
                "s3", config=botocore.client.Config(signature_version=signature_version),
            )
        else:
            self.s3 = boto3.resource(
                "s3", config=botocore.client.Config(signature_version=signature_version),
            )
        self.db_hash = None
        self.load_remote_db()

    def close(self, *args, **kwargs):
        """
        Engine closed, copy file to DB if it has changed
        """
        super(DatabaseWrapper, self).close(*args, **kwargs)

        file_bytes = _get_bytes(self.settings_dict["NAME"])
        current_md5 = _get_md5(file_bytes)
        if self.db_hash == current_md5:
            log.debug("Database unchanged, not saving to remote DB!")
            return
        log.debug(
            "Current md5:%s, Expected md5:%s. Database changed, pushing to S3.",
            current_md5,
            self.db_hash,
        )
        try:
            self.s3.Object(
                self.settings_dict["BUCKET"], self.settings_dict["REMOTE_NAME"],
            ).put(Body=file_bytes, ContentMD5=base64.b64encode(binascii.unhexlify(current_md5)).decode("utf-8"))
            self.db_hash = current_md5
            log.debug("Saved to remote DB!")
        except Exception as e:
            log.exception("An error occurred pushing the database to S3.")
