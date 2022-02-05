from __future__ import unicode_literals

import os
import speckenv
import tempfile
import warnings
from speckenv_django import django_cache_url, django_database_url
from unittest import TestCase, expectedFailure


class EnvTestCase(TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(
                b"""
DATABASE_URL=postgres://localhost:5432/example_com
ALLOWED_HOSTS=['*']

# COMMENTED=yes
COMMENTED=no
COMMENTED=ignored

COMMENT_STR=value  # TEST
COMMENT_STR_QUOTED="value  # TEST"
COMMENT_INT=42  # TEST

NO_EQUAL_SIGN
"""
            )

            f.seek(0)

            speckenv.read_speckenv(f.name)

    def test_read(self):
        # Bare value
        self.assertEqual(os.environ.get("ALLOWED_HOSTS"), "['*']")

        # literal_eval'ed value
        self.assertEqual(speckenv.env("ALLOWED_HOSTS"), ["*"])
        self.assertEqual(speckenv.env("ALLOWED_HOSTS", coerce=tuple), ("*",))

        # First not-commented out value
        self.assertEqual(speckenv.env("COMMENTED"), "no")

        # Not defined values
        self.assertEqual(speckenv.env("UNDEFINED"), None)
        self.assertIs(speckenv.env("UNDEFINED", coerce=bool), False)
        self.assertRaises(Exception, speckenv.env, "UNDEFINED", required=True)

        # Defaults
        self.assertEqual(speckenv.env("DEFAULT"), None)
        self.assertEqual(speckenv.env("DEFAULT", default=42), 42)
        self.assertEqual(speckenv.env("COMMENTED", default=42), "no")
        self.assertIs(speckenv.env("COMMENTED", default="bla", coerce=bool), True)

        self.assertNotIn("NO_EQUAL_SIGN", os.environ)

    @expectedFailure
    def test_inline_comment_str(self):
        self.assertEqual(speckenv.env("COMMENT_STR"), "value")

    def test_inline_comment_str_quoted(self):
        self.assertEqual(speckenv.env("COMMENT_STR_QUOTED"), "value  # TEST")

    def test_inline_comment_int(self):
        # Works because ast.literal_eval also knows how to handle comments...
        self.assertEqual(speckenv.env("COMMENT_INT"), 42)


class CustomMappingTestCase(TestCase):
    def test_custom_mapping(self):
        mapping = {}
        with tempfile.NamedTemporaryFile() as f:
            f.write(
                b"""
CUSTOM_MAPPING=yes
"""
            )

            f.seek(0)

            speckenv.read_speckenv(f.name, mapping=mapping)

        self.assertNotIn("CUSTOM_MAPPING", os.environ)

        self.assertEqual(speckenv.env("CUSTOM_MAPPING", mapping=mapping), "yes")


class WarningsTestCase(TestCase):
    def test_no_file(self):
        i = 0
        while True:
            filename = "env-{}".format(i)
            if not os.path.exists(filename):
                break
            i = i + 1  # pragma: no cover

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            speckenv.read_speckenv(filename)

            self.assertEqual(len(w), 1)
            self.assertIn(
                "{} not a file, not reading anything".format(filename),
                "{}".format(w[0].message),
            )

    def test_not_exists(self):
        mapping = {"EXISTS": True}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            speckenv.env("EXISTS", mapping=mapping, warn=True)
            speckenv.env("NOT", mapping=mapping, warn=True)

            self.assertEqual(len(w), 1)
            self.assertIn(
                "Key 'NOT' not available in environment", "{}".format(w[0].message)
            )


class TwelveFactorTestCase(TestCase):
    def setUp(self):
        self.mapping = {}

        with tempfile.NamedTemporaryFile() as f:
            f.write(
                b"""
DATABASE_URL=postgres://example_com:feqcv97siqxwu1@localhost:5432/example_com
CACHE_URL=hiredis://localhost:6379/1/?key_prefix=example_com
EMAIL_URL=submission://no-reply@example_com:8p7f%21Y%40do6@smtp.mailgun.com:587/
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

    def test_parse_cache_url(self):
        url = speckenv.env("CACHE_URL", mapping=self.mapping)

        self.assertEqual(
            django_cache_url(url),
            {
                "ENGINE": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://localhost:6379",
                "KEY_PREFIX": "example_com",
                "OPTIONS": {"db": "1"},
            },
        )
