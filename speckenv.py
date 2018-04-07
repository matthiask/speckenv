# Thanks to the authors of django-dotenv and django-getenv for the inspiration!

import ast
import os
import warnings


def read_speckenv(filename='.env', mapping=os.environ):
    """
    Writes the values in ``.env`` in the current working folder into
    ``os.environ`` (or a different ``mapping``) if the keys do not exist
    already.

    Example::

        DATABASE_URL=...
        CACHE_URL = '...'
        SECRET_KEY = "...."
        # Ignored
    """
    path = os.path.join(
        os.getcwd(),
        filename)
    if not os.path.isfile(path):
        warnings.warn('%s not a file, not reading anything' % filename)
        return
    # Not sure whether we should try handling other encodings than ASCII
    # at all...
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = [v.strip('\'" \t') for v in line.split('=', 1)]
            mapping.setdefault(key, value)


def env(key, default=None, required=False, mapping=os.environ, coerce=None):
    """
    An easier way to read values from the environment (or from a different
    ``mapping``). Knows how to convert literals such as ``42``, ``None`` or
    ``[1, 2, 'c']`` into the correct type.
    """
    if coerce is None:
        coerce = lambda x: x
    try:
        value = mapping[key]
        return coerce(ast.literal_eval(value))
    except (SyntaxError, ValueError):
        return coerce(value)
    except KeyError:
        if required:
            raise Exception(
                'Required key %s not available in environment'
                % repr(key))
        return coerce(default)
