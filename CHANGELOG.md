# Changelog

## 2.2.0 — 2026-09-30

- **Configuration health.** `GET /api/munin/v2/health/` (IsAdminUser) aggregates every Django system check
  tagged `entirius_config` into rows (`code`, `module`, `state`, `severity`, `title`, `detail`, `fix_url`,
  `scope`); `POST /api/munin/v2/health/check/` adds the live probes (tag `entirius_probe`). The AI toolbox is
  the first check, `toolbox.status`. CLI: `manage.py check --database default --tag entirius_config`.
- **Deprecated:** `platform.toolbox_status` on `GET /api/munin/v2/` — read `toolbox.status` from `health/`
  instead (entirius-pwa-cms does from the same release). Still sent, so an older CMS keeps its toolbox banner
  after a munin upgrade; removed in 3.0.0.

## 2.1.0 — 2026-09-15

- `GET /api/munin/v2/` carries `platform.toolbox_status` (`configured` /
  `unconfigured` / `unreachable`, from `django_utils.toolbox.status()`), so the
  CMS can tell whether AI actions are usable. `null` when the toolbox client
  is not installed (`entirius-django-utils` < 2.1.0). Computed per request,
  outside munin's response cache; `status()` caches its own probe for 60 s.
  Additive: every existing field is unchanged.
- Docs: module overview for the portal (`docs/index.md`), this changelog.
- `.github/CODEOWNERS`: `@entirius/maintainers-backend`.

## 2.0.0 — 2026-07-10

- Initial public release: module discovery (`is_volkanos` AppConfig flag plus
  structural introspection), the `Module` registry with admin-controlled
  `enabled_in_cms` / `display_order` / `config`, and the `ConfigEntry`
  runtime key-value store.
- REST API at `/api/munin/v2/` (public module list, admin config entries)
  with response caching and signal-driven invalidation.
- Discovery runs automatically after every `migrate`; `discover_modules`
  stays available for manual re-scans.
