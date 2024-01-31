from unittest import TestCase

from speckenv_django import django_cache_url


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

    def test_parse_redis_with_replicas(self):
        url = (
            "redis://10.0.0.1:6379,10.0.0.2:6379,10.0.0.3:6379/?key_prefix=example_com"
        )
        self.assertEqual(
            django_cache_url(url),
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": [
                    "redis://10.0.0.1:6379",
                    "redis://10.0.0.2:6379",
                    "redis://10.0.0.3:6379",
                ],
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

    def test_parse_unknown(self):
        with self.assertRaises(KeyError):
            django_cache_url("unknown://")
