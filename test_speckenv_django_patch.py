import os
import sys
import warnings
from unittest import TestCase

from speckenv_django_patch import (
    patch_dj_database_url,
    patch_dj_email_url,
    patch_django_cache_url,
)


class DjangoPatchTest(TestCase):
    def test_patch(self):
        modules = sys.modules.copy()

        patch_dj_database_url()
        patch_django_cache_url()
        patch_dj_email_url()

        self.assertIs(sys.modules["dj_database_url"], modules["dj_database_url"])
        self.assertIs(sys.modules["django_cache_url"], modules["django_cache_url"])
        self.assertIs(sys.modules["dj_email_url"], modules["dj_email_url"])

        os.environ.pop("DATABASE_URL", None)
        with self.assertRaises(SystemExit):
            sys.modules["dj_database_url"].config()

        os.environ["CACHE_URL"] = "locmem://"
        cfg = sys.modules["django_cache_url"].config()
        self.assertEqual(
            cfg["BACKEND"],
            "django.core.cache.backends.locmem.LocMemCache",
        )

        os.environ.pop("EMAIL_URL", None)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with self.assertWarnsRegex(Warning, r"Key 'EMAIL_URL' not available"):
                cfg = sys.modules["dj_email_url"].config()

        self.assertEqual(
            cfg["EMAIL_BACKEND"],
            "django.core.mail.backends.smtp.EmailBackend",
        )
