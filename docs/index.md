---
title: Munin
description: Module discovery and runtime configuration — auto-detects installed Volkanos modules and serves them via REST API.
sidebar:
  label: Overview
  collapsed: true
---

django-munin is the platform's module registry. It scans `INSTALLED_APPS` for Volkanos modules (AppConfigs with `is_volkanos = True`), introspects their structure — models, API, admin API, channels, translations, fixtures — and persists the result to a `Module` table served over REST. Frontends read this instead of hardcoding module lists: the CMS sidebar shows exactly the panels the backend actually runs.

## What It Does

- Discovers Volkanos apps and introspects capabilities (`has_models`, `has_api`, `has_admin_api`, `has_channels`, `has_translations`, ...)
- Upserts `Module` rows — auto-detected fields are overwritten on every scan, admin-controlled fields (`enabled_in_cms`, `display_order`, `config`) are preserved
- Deactivates modules removed from `INSTALLED_APPS` (`is_active=False`, config kept for re-addition)
- Runs automatically after every `migrate` via a `post_migrate` receiver (since 1.1.0); manual re-scan via `manage.py discover_modules`
- Serves runtime key-value configuration (`ConfigEntry`) for admins

## API Surface

Prefix `/api/munin/v2/`:

| Method | Endpoint | Access |
|---|---|---|
| GET | `/` | AllowAny — public fields; admins (JWT + staff) additionally get `enabled_in_cms`, `display_order`, `app_label` |
| GET | `/{key}/` | AllowAny — single module by key |
| GET/POST | `/admin/entries/` | IsAdminUser — config entries (paginated) |
| PATCH/DELETE | `/admin/entries/{key}/` | IsAdminUser |

Responses are cached (`MUNIN_CACHE_TTL`, default 300s); cache invalidates via post_save/post_delete signals on `Module` and `ConfigEntry`.

## Toolbox Status

The module list carries `platform.toolbox_status` — whether the AI toolbox is usable on this instance:

| Value | Meaning |
|---|---|
| `configured` | toolbox settings present and the toolbox answered its model-catalogue probe |
| `unconfigured` | `AI_TOOLBOX_BASE_URL`, `AI_TOOLBOX_API_KEY` or `AI_TOOLBOX_CHANNEL` is empty — no network call |
| `unreachable` | settings present, but the probe failed (network, auth, 5xx) |
| `null` | the toolbox client (`django_utils.toolbox`, `entirius-django-utils` ≥ 2.1.0) is not installed |

The value comes from `django_utils.toolbox.status()` and is added per request, outside munin's response
cache; the probe result itself is cached for 60 s by `django_utils`. Munin never hard-imports the toolbox.
The CMS uses it to show or hide AI actions.

## Consumers

- **cms-blueprint** — panel enablement (`useMuninStore`, `GET /api/munin/v2/`); `enabled_in_cms` toggled in Django admin drives the CMS sidebar
- Other modules — runtime config via `config_service.get_config_value()` (consume with `try/except ImportError`)

## Dependencies

- `django-utils` — `BaseModel` timestamps; optionally `django_utils.toolbox` for `platform.toolbox_status`
