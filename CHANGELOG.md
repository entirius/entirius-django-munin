# Changelog

## 2.0.0 — 2026-07-10

- Initial public release: module discovery (`is_volkanos` AppConfig flag plus
  structural introspection), the `Module` registry with admin-controlled
  `enabled_in_cms` / `display_order` / `config`, and the `ConfigEntry`
  runtime key-value store.
- REST API at `/api/munin/v2/` (public module list, admin config entries)
  with response caching and signal-driven invalidation.
- Discovery runs automatically after every `migrate`; `discover_modules`
  stays available for manual re-scans.
