# Thanks to the authors of django-dotenv and django-getenv for the inspiration!

import ast
import os
import sys
import warnings
from typing import Any, Callable, MutableMapping, TypeVar, Union


T = TypeVar("T")


def read_speckenv(
    filename: str = ".env", *, mapping: MutableMapping[str, str] = os.environ
) -> None:
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
    path = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(path):
        warnings.warn(f"{filename} not a file, not reading anything", stacklevel=2)
        return
    # Not sure whether we should try handling other encodings than ASCII
    # at all...
    with open(path) as f:
        lines = (line.strip() for line in f)
        for line in lines:
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = tuple(v.strip(" \t") for v in line.split("=", 1))
            mapping.setdefault(key, value)


def identity(x: T) -> T:
    return x


def env(
    key: str,
    *,
    default: T = None,
    required: bool = False,
    mapping: MutableMapping[str, str] = os.environ,
    coerce: Callable[[Any], Any] = identity,
    warn: Union[bool, str] = False,
) -> T:
    """
    An easier way to read values from the environment (or from a different
    ``mapping``). Knows how to convert literals such as ``42``, ``None`` or
    ``[1, 2, 'c']`` into the correct type.
    """
    try:
        value = mapping[key]
        return coerce(ast.literal_eval(value))
    except (SyntaxError, ValueError):
        return coerce(value)
    except KeyError:
        if warn is True:
            warnings.warn(f"Key '{key}' not available in environment", stacklevel=2)
        elif warn:
            warnings.warn(
                f"Key '{key}' not available in environment ({warn})",
                stacklevel=2,
            )
        if required:
            sys.exit(f"Exiting: Required key '{key}' missing")
        return coerce(default)
