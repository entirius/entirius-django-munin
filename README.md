# django-munin

Module discovery and runtime configuration for Volkanos — auto-discovers installed Volkanos modules,
introspects their capabilities (models, API, channels, translations…), persists them to the database
and serves the result via REST API together with runtime key-value configuration entries.

## Installation

```shell
pip install entirius-django-munin
```

Add the app to your project:

```python
INSTALLED_APPS = [
    ...
    "django_munin",
]
```

Discovery runs automatically after every `migrate`; manual re-scan:

```shell
python manage.py discover_modules
```

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Development and agent instructions: [AGENTS.md](AGENTS.md).

## License

Mozilla Public License 2.0 — see [LICENSE](LICENSE).
