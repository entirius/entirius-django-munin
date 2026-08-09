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

## Consumers

- **cms-blueprint** — panel enablement (`useMuninStore`, `GET /api/munin/v2/`); `enabled_in_cms` toggled in Django admin drives the CMS sidebar
- Other modules — runtime config via `config_service.get_config_value()` (consume with `try/except ImportError`)

## Dependencies

- `django-utils` — `BaseModel` timestamps
