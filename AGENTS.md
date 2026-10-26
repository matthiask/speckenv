# Agent notes

- Run tests: `python -m unittest discover -v` (or `tox` for all Python versions).
- Lint/format: `uvx ruff check .` and `uvx ruff format .` (also run via pre-commit).
- Tests against a real Django version (Django isn't a dependency), e.g.:
  `uv run --no-project --with "django==6.1" python -W error script.py`
- `test_speckenv_django_compat.py` loads the generated settings into Django;
  it's skipped without Django. Run e.g. `uvx --with tox-uv tox -e py313-dj61`
  (see `tox.ini` for all Django environments).
- Add user-facing changes to the "Next version" section of `CHANGELOG.rst`.
- Commit feature by feature, with short messages that don't repeat what the
  diff shows, and without attribution (no Co-Authored-By lines).
