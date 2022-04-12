"""
Insert the following line at the top of your settings file to use this::

    import speckenv_django_patch  # noqa isort:skip

Or better yet, convert the code to use speckenv_django directly.
"""

import sys
from types import ModuleType

from speckenv import env
from speckenv_django import django_cache_url, django_database_url, django_email_url


def patch_dj_database_url():
    if "dj_database_url" in sys.modules:
        return

    m = ModuleType("dj_database_url")
    m.config = lambda name="DATABASE_URL": django_database_url(env(name, required=True))
    m.parse = django_database_url
    sys.modules["dj_database_url"] = m


def patch_django_cache_url():
    if "django_cache_url" in sys.modules:
        return

    m = ModuleType("django_cache_url")
    m.config = lambda name="CACHE_URL": django_cache_url(
        env(name, default="locmem://", warn=True)
    )
    m.parse = django_cache_url
    sys.modules["django_cache_url"] = m


def patch_dj_email_url():
    if "dj_email_url" in sys.modules:
        return

    m = ModuleType("dj_email_url")
    m.config = lambda name="EMAIL_URL", default="smtp://": django_email_url(
        env(name, default=default, warn=True)
    )
    m.parse = django_email_url
    sys.modules["dj_email_url"] = m


patch_dj_database_url()
patch_django_cache_url()
patch_dj_email_url()
