from pathlib import Path
from unittest import TestCase

from speckenv_django import django_storage_url


class DjangoStorageURLTest(TestCase):
    maxDiff = None

    def test_parse_storage_url(self):
        url = "file:/test/media/"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {
                    "base_url": None,
                    "location": Path("/test/media/"),
                },
            },
        )

    def test_parse_storage_url_with_url(self):
        url = "file:/test/media/?base_url=/media/"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {
                    "base_url": "/media/",
                    "location": Path("/test/media/"),
                },
            },
        )

    def test_parse_relative_url(self):
        cwd = Path("/hello/world/")
        url = "file:./relative/"
        self.assertEqual(
            django_storage_url(url, base_dir=cwd),
            {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {
                    "base_url": None,
                    "location": Path("/hello/world/relative/"),
                },
            },
        )

    def test_parse_s3_vhost(self):
        url = "s3://access-key-id:secret-access-key@bucket.name.s3.eu-central-1.amazonaws.com/media/"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django_s3_storage.storage.S3Storage",
                "OPTIONS": {
                    "aws_region": "eu-central-1",
                    "aws_access_key_id": "access-key-id",
                    "aws_secret_access_key": "secret-access-key",
                    "aws_s3_bucket_name": "bucket.name",
                    "aws_s3_key_prefix": "media",
                },
            },
        )

    def test_parse_s3_path(self):
        url = "s3://access-key-id:secret-access-key@s3.eu-central-1.amazonaws.com/bucket-name/media/"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django_s3_storage.storage.S3Storage",
                "OPTIONS": {
                    "aws_region": "eu-central-1",
                    "aws_access_key_id": "access-key-id",
                    "aws_secret_access_key": "secret-access-key",
                    "aws_s3_bucket_name": "bucket-name",
                    "aws_s3_key_prefix": "media",
                },
            },
        )

    def test_other_s3_nine(self):
        # https://docs.nine.ch/docs/object-storage/object-storage-client-tools
        url = "s3://6aaf50b17357446bb:fcf1c9c6bc5c43@cz42.objectstorage.nineapis.ch/bucket-etj4mwc/thing/?aws_region=nine-cz42"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django_s3_storage.storage.S3Storage",
                "OPTIONS": {
                    "aws_s3_endpoint_url": "https://cz42.objectstorage.nineapis.ch",
                    "aws_region": "nine-cz42",
                    "aws_access_key_id": "6aaf50b17357446bb",
                    "aws_secret_access_key": "fcf1c9c6bc5c43",
                    "aws_s3_bucket_name": "bucket-etj4mwc",
                    "aws_s3_key_prefix": "thing",
                },
            },
        )

    def test_other_s3_digitalocean(self):
        # https://docs.digitalocean.com/reference/api/spaces-api/
        url = "s3://access-key:secret-key@nyc3.digitaloceanspaces.com/example-space-name/key-prefix/?aws_region=nyc3"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django_s3_storage.storage.S3Storage",
                "OPTIONS": {
                    "aws_access_key_id": "access-key",
                    "aws_secret_access_key": "secret-key",
                    "aws_region": "nyc3",
                    "aws_s3_key_prefix": "key-prefix",
                    "aws_s3_endpoint_url": "https://nyc3.digitaloceanspaces.com",
                    "aws_s3_bucket_name": "example-space-name",
                },
            },
        )

    def test_s3_parameters(self):
        url = "s3://access-key-id:secret-access-key@bucket-name.s3.eu-central-1.amazonaws.com/media/?aws_s3_public_auth=False&aws_s3_gzip=True&aws_s3_connect_timeout=120"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django_s3_storage.storage.S3Storage",
                "OPTIONS": {
                    "aws_region": "eu-central-1",
                    "aws_access_key_id": "access-key-id",
                    "aws_secret_access_key": "secret-access-key",
                    "aws_s3_bucket_name": "bucket-name",
                    "aws_s3_key_prefix": "media",
                    # Types!
                    "aws_s3_public_auth": False,
                    "aws_s3_gzip": True,
                    "aws_s3_connect_timeout": 120,
                },
            },
        )
