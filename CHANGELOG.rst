==========
Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

- Added type hints.
- Raised the minimum Python version to 3.8.


`2.0`_ (2021-11-05)
~~~~~~~~~~~~~~~~~~~

- Renamed the main branch to main.
- Switched from Travis CI to GitHub actions.
- Raised the minimum Python version to 3.6. Added 3.10.
- Made all but the first argument to ``env`` (and ``read_speckenv``)
  keyword-only.
- Converted the package to use a declarative setup.


`1.4`_ (2020-09-01)
~~~~~~~~~~~~~~~~~~~

- Raised code coverage to 100%.
- Removed an usage of ``repr()`` to avoid differences between Python 2
  and 3.
- Verified support for Python 3.7, 3.8 and 3.9.


`1.3`_ (2018-10-10)
~~~~~~~~~~~~~~~~~~~

- Reformat the code using black.
- Added a ``warn`` parameter to ``env`` which causes warnings to be
  emitted when a variable isn't set in the environment.


`1.2`_ (2018-04-07)
~~~~~~~~~~~~~~~~~~~

- Added the ``coerce`` parameter to ``env`` to allow coercion of values.


`1.1`_ (2017-07-17)
~~~~~~~~~~~~~~~~~~~

- Added a testsuite and configuration for running the tests on Travis
  CI.
- Added the possibility to override the environment dictionary used (may
  be useful if ``os.environ`` should not be modified)


`1.0`_ (2016-11-24)
~~~~~~~~~~~~~~~~~~~

- Initial release!

.. _1.0: https://github.com/matthiask/speckenv/commit/98bba642766c
.. _1.1: https://github.com/matthiask/speckenv/compare/1.0...1.1
.. _1.2: https://github.com/matthiask/speckenv/compare/1.1...1.2
.. _1.3: https://github.com/matthiask/speckenv/compare/1.2...1.3
.. _1.4: https://github.com/matthiask/speckenv/compare/1.3...1.4
.. _2.0: https://github.com/matthiask/speckenv/compare/1.4...2.0
.. _Next version: https://github.com/matthiask/speckenv/compare/2.0...main
