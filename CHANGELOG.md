## v0.2.2 (2024-07-27)

### Fix

- omit description in metadata if it is empty
- convert time_unix_nano to datetime in UTC

### Refactor

- replace models with type stubs
- convert models to Protocols

## v0.2.1 (2024-07-20)

### Fix

- fix isinstance call using wrong Histogram class

## v0.2.0 (2024-07-14)

### Feat

- add parameters dim_prefix_resource, dim_prefix_scope, batch_atomicity to OCIMetricsExporter initializer

### Fix

- fix some types of test_exporter
- fix post_metrics_data_response mock

### Refactor

- add py-typed marker
- **pyproject.toml**: add project block and sort alphabetically
- initialize poetry project
