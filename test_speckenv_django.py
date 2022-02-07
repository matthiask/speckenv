from unittest import TestCase

from speckenv_django import django_cache_url, django_database_url


# EMAIL_URL=submission://no-reply@example_com:8p7f%21Y%40do6@smtp.mailgun.com:587/


class DjangoDatabaseURLTest(TestCase):
    def test_parse_database_url(self):
        url = "postgres://example_com:feqcv97siqxwu1@localhost:5432/example_com"
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
        url = "postgres://localhost:5432/example_com"
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
        url = "mysql://%23user:%23password@ec2.amazonaws.com:5431/%23database"
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
        url = "postgres://localhost:5432/example_com?conn_max_age=10"
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
    def test_parse_cache_url(self):
        url = "hiredis://localhost:6379/1/?key_prefix=example_com"
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
        url = "hiredis://user:pass@localhost:6379/1/?key_prefix=example_com"
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
        url = "redis://127.0.0.1:6379/?key_prefix=example_com"
        self.assertEqual(
            django_cache_url(url),
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379",
                "KEY_PREFIX": "example_com",
                "OPTIONS": {},
            },
        )

    def test_parse_locmem_url(self):
        self.assertEqual(
            django_cache_url("locmem://"),
            {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "",
                "KEY_PREFIX": "",
            },
        )

    def test_parse_location_locmem_url(self):
        self.assertEqual(
            django_cache_url("locmem://snowflake?key_prefix=stuff"),
            {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "snowflake",
                "KEY_PREFIX": "stuff",
            },
        )

    def test_parse_dummy_url(self):
        self.assertEqual(
            django_cache_url("dummy://"),
            {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            },
        )
