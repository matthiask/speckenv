# Agent notes

- Run tests: `python -m unittest discover -v` (or `tox` for all Python versions).
- Lint/format: `uvx ruff check .` and `uvx ruff format .` (also run via pre-commit).
- Tests against a real Django version (Django isn't a dependency), e.g.:
  `uv run --no-project --with "django==6.1" python -W error script.py`
- Add user-facing changes to the "Next version" section of `CHANGELOG.rst`.
- Commit feature by feature, with short messages that don't repeat what the
  diff shows, and without attribution (no Co-Authored-By lines).
