import tempfile
from unittest import TestCase

import speckenv
from speckenv_django import django_cache_url, django_database_url


class DjangoDatabaseURLTest(TestCase):
    def setUp(self):
        self.mapping = {}

        with tempfile.NamedTemporaryFile() as f:
            f.write(
                b"""
DATABASE_URL=postgres://example_com:feqcv97siqxwu1@localhost:5432/example_com
LOCAL_DATABASE_URL=postgres://localhost:5432/example_com
QUOTED_DATABASE_URL=mysql://%23user:%23password@ec2.amazonaws.com:5431/%23database
MAX_AGE_DATABASE_URL=postgres://localhost:5432/example_com?conn_max_age=10
# EMAIL_URL=submission://no-reply@example_com:8p7f%21Y%40do6@smtp.mailgun.com:587/
"""
            )

            f.seek(0)

            speckenv.read_speckenv(f.name, mapping=self.mapping)

    def test_parse_database_url(self):
        url = speckenv.env("DATABASE_URL", mapping=self.mapping)

        self.assertEqual(
            django_database_url(url),
            {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "example_com",
                "USER": "example_com",
                "PASSWORD": "feqcv97siqxwu1",
                "HOST": "localhost",
                "PORT": "5432",
            },
        )

    def test_parse_local_database_url(self):
        url = speckenv.env("LOCAL_DATABASE_URL", mapping=self.mapping)

        self.assertEqual(
            django_database_url(url),
            {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "example_com",
                "USER": "",
                "PASSWORD": "",
                "HOST": "localhost",
                "PORT": "5432",
            },
        )

    def test_parse_quoted_database_url(self):
        url = speckenv.env("QUOTED_DATABASE_URL", mapping=self.mapping)

        self.assertEqual(
            django_database_url(url),
            {
                "ENGINE": "django.db.backends.mysql",
                "NAME": "#database",
                "USER": "#user",
                "PASSWORD": "#password",
                "HOST": "ec2.amazonaws.com",
                "PORT": "5431",
            },
        )

    def test_parse_max_age_database_url(self):
        url = speckenv.env("MAX_AGE_DATABASE_URL", mapping=self.mapping)

        self.assertEqual(
            django_database_url(url),
            {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "example_com",
                "USER": "",
                "PASSWORD": "",
                "HOST": "localhost",
                "PORT": "5432",
                "CONN_MAX_AGE": 10,
            },
        )


class DjangoCacheURLTest(TestCase):
    def setUp(self):
        self.mapping = {}

        with tempfile.NamedTemporaryFile() as f:
            f.write(
                b"""
CACHE_URL=hiredis://localhost:6379/1/?key_prefix=example_com
AUTH_CACHE_URL=hiredis://user:pass@localhost:6379/1/?key_prefix=example_com
NO_DB_CACHE_URL=redis://127.0.0.1:6379/?key_prefix=example_com
"""
            )

            f.seek(0)

            speckenv.read_speckenv(f.name, mapping=self.mapping)

    def test_parse_cache_url(self):
        url = speckenv.env("CACHE_URL", mapping=self.mapping)

        self.assertEqual(
            django_cache_url(url),
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://localhost:6379",
                "KEY_PREFIX": "example_com",
                "OPTIONS": {"db": "1"},
            },
        )

    def test_parse_auth_cache_url(self):
        url = speckenv.env("AUTH_CACHE_URL", mapping=self.mapping)

        self.assertEqual(
            django_cache_url(url),
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://user:pass@localhost:6379",
                "KEY_PREFIX": "example_com",
                "OPTIONS": {"db": "1"},
            },
        )

    def test_parse_no_db_cache_url(self):
        url = speckenv.env("NO_DB_CACHE_URL", mapping=self.mapping)

        self.assertEqual(
            django_cache_url(url),
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379",
                "KEY_PREFIX": "example_com",
                "OPTIONS": {},
            },
        )
