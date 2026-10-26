"""
Feeds the output of speckenv_django into an actual Django installation. Skipped
when Django isn't installed, use e.g. ``tox -e py313-dj61`` to run the tests.
"""

import os
import shutil
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path
from types import ModuleType
from unittest import TestCase, skipUnless

from speckenv_django import (
    django_cache_url,
    django_database_url,
    django_email_url,
    django_mailer_url,
    django_storage_url,
)


try:
    import django
except ImportError:  # pragma: no cover
    django = None

VERSION = django.VERSION if django else (0,)
HAS_POSTGRES = bool(find_spec("psycopg") or find_spec("psycopg2"))
HAS_REDIS = bool(find_spec("redis"))
SETTINGS_MODULE = "speckenv_django_compat_settings"

TMP_DIR = Path(tempfile.mkdtemp())


def setUpModule():
    if not django:
        return

    settings = ModuleType(SETTINGS_MODULE)
    settings.SECRET_KEY = "secret"
    settings.USE_TZ = True
    settings.INSTALLED_APPS = []
    settings.DATABASES = {
        "default": django_database_url("sqlite://:memory:"),
        "absolute": django_database_url(f"sqlite:///{TMP_DIR}/db.sqlite3"),
        "postgres": django_database_url(
            "postgres://us%40er:pa%23ss@db.example.com:6543/example?conn_max_age=60"
        ),
    }
    settings.CACHES = {
        "default": django_cache_url("locmem://speckenv"),
        "dummy": django_cache_url("dummy://"),
    }
    if VERSION >= (4, 0):
        settings.CACHES["redis"] = django_cache_url(
            "redis://user:pass@10.0.0.1:6379,10.0.0.2:6380/2"
            "?key_prefix=example&socket_timeout=2&health_check_interval=30"
        )

    if VERSION >= (6, 1):
        # The EMAIL_* settings are deprecated
        settings.MAILERS = {
            "default": django_mailer_url(
                "submission://us%40er:pa%23ss@smtp.example.com?timeout=5"
            ),
            "ssl": django_mailer_url(
                "smtp://smtp.example.com:465?ssl&ssl_certfile=/etc/cert.pem"
            ),
            "console": django_mailer_url("console://"),
            "locmem": django_mailer_url("locmem://"),
        }
    else:
        for key, value in django_email_url(
            "submission://us%40er:pa%23ss@smtp.example.com"
            "?timeout=5&_default_from_email=from@example.com"
        ).items():
            setattr(settings, key, value)

    if VERSION >= (4, 2):
        settings.STORAGES = {
            "default": django_storage_url("file:media/", base_dir=TMP_DIR),
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }

    sys.modules[SETTINGS_MODULE] = settings
    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS_MODULE
    django.setup()


def tearDownModule():
    if django:
        from django.db import connections

        connections.close_all()
    shutil.rmtree(TMP_DIR, ignore_errors=True)


@skipUnless(django, "Django isn't installed")
class DatabaseTest(TestCase):
    def test_sqlite(self):
        from django.db import connections

        for alias in ["default", "absolute"]:
            with self.subTest(alias=alias), connections[alias].cursor() as cursor:
                cursor.execute("SELECT 1")
                self.assertEqual(cursor.fetchone(), (1,))

        self.assertTrue((TMP_DIR / "db.sqlite3").exists())

    @skipUnless(HAS_POSTGRES, "psycopg isn't installed")
    def test_postgres(self):
        from django.db import connections

        connection = connections["postgres"]
        params = connection.get_connection_params()
        # Django < 4.2 uses "database"
        self.assertEqual(params.get("dbname", params.get("database")), "example")
        self.assertEqual(params["user"], "us@er")
        self.assertEqual(params["password"], "pa#ss")
        self.assertEqual(params["host"], "db.example.com")
        self.assertEqual(params["port"], "6543")
        self.assertEqual(connection.settings_dict["CONN_MAX_AGE"], 60)


@skipUnless(django, "Django isn't installed")
class CacheTest(TestCase):
    def test_locmem(self):
        from django.core.cache import caches

        cache = caches["default"]
        cache.set("key", "value")
        self.assertEqual(cache.get("key"), "value")

        cache = caches["dummy"]
        cache.set("key", "value")
        self.assertIsNone(cache.get("key"))

    @skipUnless(VERSION >= (4, 0), "RedisCache requires Django 4.0")
    @skipUnless(HAS_REDIS, "redis isn't installed")
    def test_redis(self):
        from django.core.cache import caches

        cache = caches["redis"]
        self.assertEqual(
            cache._servers,
            ["redis://user:pass@10.0.0.1:6379", "redis://user:pass@10.0.0.2:6380"],
        )
        self.assertEqual(cache.make_key("key"), "example:1:key")

        # Instantiating a connection validates the options without connecting
        for write in [True, False]:
            pool = cache._cache._get_connection_pool(write=write)
            connection = pool.make_connection()
            self.assertEqual(int(connection.db), 2)
            self.assertEqual(connection.username, "user")
            self.assertEqual(connection.password, "pass")
            self.assertEqual(connection.socket_timeout, 2)
            self.assertEqual(connection.health_check_interval, 30)


@skipUnless(django, "Django isn't installed")
@skipUnless(VERSION < (6, 1), "The EMAIL_* settings are deprecated")
class EmailTest(TestCase):
    def test_email(self):
        from django.conf import settings
        from django.core.mail import get_connection
        from django.core.mail.backends.smtp import EmailBackend

        backend = get_connection()
        self.assertIsInstance(backend, EmailBackend)
        self.assertEqual(backend.host, "smtp.example.com")
        self.assertEqual(backend.port, 587)
        self.assertEqual(backend.username, "us@er")
        self.assertEqual(backend.password, "pa#ss")
        self.assertTrue(backend.use_tls)
        self.assertFalse(backend.use_ssl)
        self.assertEqual(backend.timeout, 5)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, "from@example.com")


@skipUnless(django, "Django isn't installed")
@skipUnless(VERSION >= (6, 1), "MAILERS requires Django 6.1")
class MailerTest(TestCase):
    def test_smtp(self):
        from django.core.mail import mailers
        from django.core.mail.backends.smtp import EmailBackend

        mailer = mailers["default"]
        self.assertIsInstance(mailer, EmailBackend)
        self.assertEqual(mailer.host, "smtp.example.com")
        self.assertEqual(mailer.port, 587)
        self.assertEqual(mailer.username, "us@er")
        self.assertEqual(mailer.password, "pa#ss")
        self.assertTrue(mailer.use_tls)
        self.assertFalse(mailer.use_ssl)
        self.assertEqual(mailer.timeout, 5)

        mailer = mailers["ssl"]
        self.assertEqual(mailer.port, 465)
        self.assertTrue(mailer.use_ssl)
        self.assertFalse(mailer.use_tls)
        self.assertEqual(mailer.ssl_certfile, "/etc/cert.pem")

    def test_optionless(self):
        from django.core.mail import mailers
        from django.core.mail.backends import console, locmem

        self.assertIsInstance(mailers["console"], console.EmailBackend)
        self.assertIsInstance(mailers["locmem"], locmem.EmailBackend)


@skipUnless(django, "Django isn't installed")
@skipUnless(VERSION >= (4, 2), "STORAGES requires Django 4.2")
class StorageTest(TestCase):
    def test_file(self):
        from django.core.files.base import ContentFile
        from django.core.files.storage import FileSystemStorage, storages

        storage = storages["default"]
        self.assertIsInstance(storage, FileSystemStorage)
        self.assertEqual(Path(storage.location), TMP_DIR / "media")

        name = storage.save("hello.txt", ContentFile(b"Hello"))
        self.assertEqual((TMP_DIR / "media" / name).read_bytes(), b"Hello")
