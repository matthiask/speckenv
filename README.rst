========
speckenv
========

speckenv because a speck is a synonym for a dot and because Speck is awesome.

Usage
=====

Read the settings contained in ``./.env`` into ``os.environ`` (or a
different mapping; pass a dict-like object as ``mapping``)::

    from speckenv import read_speckenv

    read_speckenv()

Note that ``read_speckenv`` uses ``os.environ.setdefault`` to set new values,
which means that if a particular key exists more than once in the file the
first value is retained, not the last.

If the file is named differently or resides in a different path, pass the
full path as first argument to ``read_speckenv``.

Read individual values::

    from speckenv import env

    SETTING1 = env('SETTING1')
    SETTING2 = env('SETTING2', default='bla')
    SETTING3 = env('SETTING3 ', required=True)  # Fail hard if missing.
    SETTING4 = env('SETTING4', coerce=bool)  # Coercion is also applied
                                             # to default values

    # Different mapping: env('SOMETHING', mapping=...)

The following values are evaluated as Python literals::

    BOOL=True  # And False, None etc.
    NUMBER=42
    SWEET_HOME=['localhost', '127.0.0.1']

Additional whitespace around the equals sign is supported. Empty lines and
lines starting with a ``#`` are ignored.

**NOTE!** You should treat everything except for the first argument to
both ``env`` and ``read_speckenv`` as keyword-only. Since speckenv still
supports Python 2 this isn't enforced by the code right now.
