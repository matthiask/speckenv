========
speckenv
========

speckenv because a speck is a synonym for a dot and because Speck is awesome.

Usage
=====

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

    # Fallback, if SETTING2 is not set (truthyness doesn't matter):
    SETTING2 = env("SETTING2", default="bla")

    # Fail hard if missing:
    SETTING3 = env("SETTING3", required=True)

    # Coerce the value before returning it (coercion is also applied to
    # default values):
    SETTING4 = env("SETTING4", coerce=bool)

The following values are evaluated as Python literals::

    BOOL=True  # And False, None etc.
    NUMBER=42
    SWEET_HOME=["localhost", "127.0.0.1"]

Additional whitespace around the equals sign is supported. Empty lines and
lines starting with a ``#`` are ignored::

    THIS_IS_IGNORED
    # COMMENTED_OUT=VALUE
    THIS = WORKS

**NOTE!** You should treat everything except for the first argument to
both ``env`` and ``read_speckenv`` as keyword-only. Since speckenv still
supports Python 2 this isn't enforced by the code right now.

It may be useful to use a mapping separate from ``os.environ``. This is
easily possible by overriding the default mapping argument:

.. code-block:: python

    from speckenv import env, read_speckenv

    mapping = {}
    read_speckenv("file_with_variables.env", mapping=mapping)
    setting1 = env("SETTING1", mapping=mapping)
