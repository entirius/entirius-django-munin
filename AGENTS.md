# AGENTS.md

Module discovery and runtime configuration for Volkanos — distribution `entirius-django-munin`,
Django app `django_munin`. Auto-discovers installed Volkanos modules via `is_volkanos = True` flag
on AppConfig, introspects their structure (models, API, channels, translations…), persists to DB,
and serves via REST API. Frontends read this instead of hardcoding module lists.

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest + pytest-django) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the package / Django app_label / DB table prefix `django_munin` — it is a schema contract.
- Migrations are part of the public contract — never edit an already released migration.
- Default: do not commit — git is the user's call.

## Architecture

- `models/` — `Module` (auto-detected capabilities + admin settings), `ConfigEntry` (runtime
  key-value config, dotted keys, JSON values).
- `introspection.py` — pure detection functions (`has_models`, `has_api`, …).
- `services/` — `discovery_service.scan_modules()` (introspect + upsert), `config_service`
  (aggregation, caching, ConfigEntry CRUD).
- `schemas/` — pydantic request/response schemas.
- `api/` — `MuninViewSet` (AllowAny; admin JWT gets extra fields), `ConfigEntryViewSet`
  (JWT + IsAdminUser), pagination, permissions; root prefix `api/munin/v2/`.
- `management/commands/discover_modules.py` — manual re-scan entry point.

Layer rule: `API → Services → Models → DB`. No ORM in views.

## Gotchas

- Discovery runs automatically after every `migrate` via a `post_migrate` receiver in `apps.py`.
  Do NOT call `scan_modules()` from `AppConfig.ready()` — ready() fires before tables exist.
- Auto-detected fields (`has_*`, label, version) are overwritten on every scan; admin-controlled
  fields (`enabled_in_cms`, `display_order`, `config`) are set on first create and preserved.
- Modules removed from INSTALLED_APPS get `is_active=False`, never deleted — config survives re-adding.
- Consumers of `config_service.get_config_value()` should guard with `try/except ImportError`.
- Cache invalidation is version-bumping via post_save/post_delete signals; all signals carry `dispatch_uid`.
