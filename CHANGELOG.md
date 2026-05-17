# Changelog

## [2.0.0] - 2026-05-17

### Added
- Pagination support (limit/offset) for all _info modules
- 3 operational roles for Databricks platform
- Notebook and sql_query modules to fill coverage gaps
- Comprehensive README with module index, EDA, and examples
- Comprehensive unit and integration test suites
- Pre-commit and linting configuration (ruff, ansible-lint)

### Fixed
- cluster_event_info documentation repaired
- Options block issues, duplicate options, doc defaults, and no_log fixed
- Boilerplate, namespace, meta versions, lint config added
- Role README files added for Galaxy compliance
- Galaxy import validation issues resolved
- CI failures resolved across Python 3.11-3.13

### Changed
- Auto-formatted all modules with ruff
- Expanded ruff ignore list for compatibility
- Excluded roles from ansible-lint syntax-check

## [1.0.0] - 2026-05-15

### Added
- 105 modules covering full Databricks platform API (workspaces, clusters, jobs, MLflow, serving, governance)
- CRUD + info module for every resource type
- EDA source plugins for event-driven automation
- Unit tests and CI pipeline
