from unittest import TestCase

from speckenv_django import InvalidURLError, django_storage_url


class DjangoStorageURLTest(TestCase):
    maxDiff = None

    def test_parse_storage_url(self):
        url = "file:///test/media/"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {
                    "base_url": None,
                    "location": "/test/media/",
                },
            },
        )

    def test_parse_storage_url_with_url(self):
        url = "file:///test/media/?base_url=/media/"
        self.assertEqual(
            django_storage_url(url),
            {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {
                    "base_url": "/media/",
                    "location": "/test/media/",
                },
            },
        )

    def test_parse_s3(self):
        url = "s3://access-key-id:secret-access-key@bucket-name.s3.eu-central-1.amazonaws.com/media/"
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

    def test_invalid_s3(self):
        with self.assertRaises(InvalidURLError):
            django_storage_url("s3://s3.eu-central-1.amazonaws.com/bucket")

    def test_other_s3(self):
        # https://docs.nine.ch/docs/object-storage/object-storage-client-tools
        url = "s3://6aaf50b17357446bb:fcf1c9c6bc5c43@bucket-etj4mwc.s3.nine-cz42.amazonaws.com?aws_s3_endpoint_url=https://cz42.objectstorage.nineapis.ch"
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
                    "aws_s3_key_prefix": "",
                },
            },
        )
