========
speckenv
========

speckenv because a speck is a synonym for a dot and because Speck is awesome.

Usage
=====

Basic
~~~~~

Read the settings contained in ``./.env`` into ``os.environ``:

.. code-block:: python

    from speckenv import read_speckenv

    read_speckenv()

Note that ``read_speckenv`` uses ``os.environ.setdefault`` to set new values,
which means that if a particular key exists more than once in the file the
first value is retained, not the last.

If the file is named differently or resides in a different path, pass the
full path as first argument to ``read_speckenv``.

Read individual values:

.. code-block:: python

    from speckenv import env

    # Standard usage:
    SETTING1 = env("SETTING1")

    # Fallback if SETTING2 does not exist:
    SETTING2 = env("SETTING2", default="bla")

    # Fail hard if missing:
    SETTING3 = env("SETTING3", required=True)

    # Coerce the value before returning it (coercion is also applied to
    # default values):
    SETTING4 = env(
        "SETTING4",
        coerce=lambda value: date(*(int(part) for part in value.split("-"))),
        default="1970-01-01",
    )

The following values are evaluated as Python literals, therefore coercing
values may be useful less often than you might think::

    BOOL=True  # And False, None etc.
    NUMBER=42
    SWEET_HOME=["localhost", "127.0.0.1"]

Additional whitespace around the equals sign is supported. Empty lines and
lines starting with a ``#`` are ignored::

    THIS_IS_IGNORED
    # COMMENTED_OUT=VALUE
    THIS = WORKS

You shouldn't use comments in lines though. They sometimes work by accident but
it's a bad idea.

If a value looks like a Python type but you want to load it as a string you
have to use coercion, e.g.

.. code-block:: python

   NUMBER_AS_STRING = env("NUMBER", coerce=str)

   # Alternatively, read the value directly from os.environ:
   NUMBER_AS_STRING = os.environ["NUMBER"]


Custom mapping instead of ``os.environ``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It may be useful to use a mapping separate from ``os.environ``. This is
easily possible by overriding the default mapping argument:

.. code-block:: python

    from speckenv import env, read_speckenv

    mapping = {}
    read_speckenv("file_with_variables.env", mapping=mapping)
    setting1 = env("SETTING1", mapping=mapping)


Django support
==============

speckenv comes with a few utilities for configuring Django using environment
variables. These are all pure functions without any side effects and no
dependency on their environment. They are only bundled with ``speckenv``
because they are useful and because it's convenient to do so.

Many other projects exist which already do this but ``speckenv_django`` is
different in that it only covers interesting settings. Also, the implementation
doesn't add monkey patches to ``urllib.parse``.

speckenv doesn't depend on Django, if you don't want to use Django or the
``speckenv_django`` module you're not paying anything besides a few KiB on the
harddisk.


``django_cache_url``
~~~~~~~~~~~~~~~~~~~~

Covers configuring a Redis, locmem or dummy cache backend with optional
authentication credentials. The Redis configuration only supports Django 4 or
better. ``redis://`` and ``hiredis://`` are equivalent since recent enough
versions of redis-py automatically select the hiredis parser if it is
available.

.. code-block:: python

    from speckenv import env
    from speckenv_django import django_cache_url

    # CACHE_URL=hiredis://localhost:6379/1/?key_prefix=example_com"
    CACHES = {"default": django_cache_url(env("CACHE_URL", default="locmem://"))}
    # NOTE! locmem:// may be a bad default, but that's up to you really.


``django_database_url``
~~~~~~~~~~~~~~~~~~~~~~~

Covers configuring a PostgreSQL, PostGIS or sqlite database engine with
authentication credentials.

.. code-block:: python

    from speckenv import env
    from speckenv_django import django_database_url

    # DATABASE_URL=postgres://localhost:5432/example_com
    DATABASES = {"default": django_database_url(env("DATABASE_URL", required=True))}


``django_email_url``
~~~~~~~~~~~~~~~~~~~~

Covers configuring an email backend. Known backends are ``smtp://``,
``submission://`` (same as ``smtp://`` but with TLS and a default port of 587),
``locmem://``, ``console://`` and ``dummy:``.

The utility also supports explicitly requesting SSL (``?ssl=true``), TLS
(``?tls=true``), SMTP timeouts (``?timeout=10``) and setting a
``DEFAULT_FROM_EMAIL`` address (``?_default_from_email=info@example.com``)

.. code-block:: python

    from speckenv import env
    from speckenv_django import django_email_url

    # DATABASE_URL=smtp://
    if DEBUG:
        globals().update(django_email_url(env("EMAIL_URL", default="console://")))
    else:
        globals().update(django_email_url(env("EMAIL_URL", default="smtp://")))


Automatically substituting other 12factor libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

speckenv ships a Python module which inserts Python modules named
``dj_database_url``, ``django_cache_url`` and ``dj_email_url`` into
``sys.modules`` (if they do not exist already) which contain basic functions
calling the functions mentioned above. This module is almost guaranteed to NOT
work in an arbitrary environment but it may be useful as a quick solution if
you do want to change the settings module as little as possible when upgrading
your code to Django 4.0 and are already using speckenv. To use it you should
insert the following line at the top of your settings module:

.. code-block:: python

    import speckenv_django_patch  # noqa isort:skip
