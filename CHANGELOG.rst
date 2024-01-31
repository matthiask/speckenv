==========
Change log
==========

Next version
~~~~~~~~~~~~

- Implemented a way to specify relative folders when using ``file:`` URLs with
  ``django_storage_url``.
- Added Python 3.12 to the CI.
- Added support for replicas to ``django_cache_url``.


6.1 (2023-11-09)
~~~~~~~~~~~~~~~~

- Made the storage URL parsing more flexible and handle more cases.


6.0 (2023-11-08)
~~~~~~~~~~~~~~~~

- Switched from black to the ruff formatter.
- Updated the pre-commit hooks.
- Added an experimental ``django_storage_url`` utility to ``speckenv_django``
  which allows configuring the bundled file system storage and also a storage
  using `django-s3-storage <https://github.com/etianen/django-s3-storage/>`__'s
  `S3Storage` backend.
- Dropped support for Python 3.8.


5.0 (2023-08-15)
~~~~~~~~~~~~~~~~

- **Backwards incompatible for edge cases:** Changed the ``.env`` file parser
  to NOT strip quotes from keys and values. This fixes the probably unexpected
  behavior where ``VALUE="42"`` produced an integer instead of a string. This
  only affects you if e.g. you added a quoted value to an ``.env`` file where
  you didn't want a string but the interpreted value. (E.g. ``COUNT="3"``).
  Just remove the quotes and you'll be good.
- Added Python 3.11 to the matrix.
- Upgraded to hatchling and ruff.


`4.0`_ (2022-08-18)
~~~~~~~~~~~~~~~~~~~

.. _4.0: https://github.com/matthiask/speckenv/compare/3.4...4.0

- Allowed warning on missing required keys.
- Changed the code to use ``sys.exit`` with a custom message when encountering
  missing required keys instead of re-raising the exception. You should not use
  ``required=True`` with values which aren't really required (use a sentinel
  value as a default instead for this uncommon use case).


`3.4`_ (2022-08-18)
~~~~~~~~~~~~~~~~~~~

.. _3.4: https://github.com/matthiask/speckenv/compare/3.3...3.4

- Added a ``speckenv_django_patch`` module to add bad knock offs of a few
  12factor apps to ``sys.modules``.
- Changed the exception type to ``KeyError`` when a required environment
  variable is missing.
- Allowed passing a warning message which is shown to the user to the ``env()``
  function, not just ``True``.


`3.3`_ (2022-03-19)
~~~~~~~~~~~~~~~~~~~

.. _3.3: https://github.com/matthiask/speckenv/compare/3.2...3.3

- Added ``django_email_url`` to the module's ``__all__`` list.
- Documented the methods of the ``speckenv_django`` module.
- Added support for the ``_server_email`` query parameter for email URLs.


`3.2`_ (2022-02-07)
~~~~~~~~~~~~~~~~~~~

.. _3.2: https://github.com/matthiask/speckenv/compare/3.1...3.2

- Added support for ``dummy://`` cache URLs.
- Added support for parsing email URLs.


`3.1`_ (2022-02-07)
~~~~~~~~~~~~~~~~~~~

.. _3.1: https://github.com/matthiask/speckenv/compare/3.0...3.1

- Added more tests to ``speckenv_django``.
- Introduced ``pre-commit`` to format all the things.
- Added support for ``locmem://`` cache URLs.


`3.0`_ (2022-02-05)
~~~~~~~~~~~~~~~~~~~

.. _3.0: https://github.com/matthiask/speckenv/compare/2.0...3.0

- Added type hints.
- Raised the minimum Python version to 3.8.
- Added a ``speckenv_django`` module containing basic and extremely opinionated
  and limited utilities to parse database and cache DSNs into configuration
  dictionaries usable by Django.


`2.0`_ (2021-11-05)
~~~~~~~~~~~~~~~~~~~

.. _2.0: https://github.com/matthiask/speckenv/compare/1.4...2.0

- Renamed the main branch to main.
- Switched from Travis CI to GitHub actions.
- Raised the minimum Python version to 3.6. Added 3.10.
- Made all but the first argument to ``env`` (and ``read_speckenv``)
  keyword-only.
- Converted the package to use a declarative setup.


`1.4`_ (2020-09-01)
~~~~~~~~~~~~~~~~~~~

.. _1.4: https://github.com/matthiask/speckenv/compare/1.3...1.4

- Raised code coverage to 100%.
- Removed an usage of ``repr()`` to avoid differences between Python 2
  and 3.
- Verified support for Python 3.7, 3.8 and 3.9.


`1.3`_ (2018-10-10)
~~~~~~~~~~~~~~~~~~~

.. _1.3: https://github.com/matthiask/speckenv/compare/1.2...1.3

- Reformat the code using black.
- Added a ``warn`` parameter to ``env`` which causes warnings to be
  emitted when a variable isn't set in the environment.


`1.2`_ (2018-04-07)
~~~~~~~~~~~~~~~~~~~

.. _1.2: https://github.com/matthiask/speckenv/compare/1.1...1.2

- Added the ``coerce`` parameter to ``env`` to allow coercion of values.


`1.1`_ (2017-07-17)
~~~~~~~~~~~~~~~~~~~

.. _1.1: https://github.com/matthiask/speckenv/compare/1.0...1.1

- Added a testsuite and configuration for running the tests on Travis
  CI.
- Added the possibility to override the environment dictionary used (may
  be useful if ``os.environ`` should not be modified)


`1.0`_ (2016-11-24)
~~~~~~~~~~~~~~~~~~~

.. _1.0: https://github.com/matthiask/speckenv/commit/98bba642766c

- Initial release!
