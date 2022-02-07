from unittest import TestCase

from speckenv_django import django_database_url


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

    def test_parse_unknown(self):
        with self.assertRaises(KeyError):
            django_database_url("unknown://")
