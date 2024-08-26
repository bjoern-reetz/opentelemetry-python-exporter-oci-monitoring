## v0.6.0 (2024-08-26)

### Feat

- add MetricsSerializer

## v0.5.0 (2024-08-26)

### BREAKING CHANGE

- Serialization of non-string values in attributes was changed.

### Refactor

- normalize sequence serialization in dimensions

## v0.4.0 (2024-08-25)

### BREAKING CHANGE

- The class was renamed to reflect the monitoring backend it is exporting. You need to update your imports - the functionality is the same.

### Feat

- add make_default_exporter convenience function

### Fix

- change type annotation of **kwargs to Any

### Refactor

- rename OCIMetricsExporter to OCIMonitoringExporter

## v0.3.0 (2024-08-04)

### BREAKING CHANGE

- Also, renamed from OCIMetricsConverter to DefaultMetricsConverter.
- Metadata now also includes the unit by default.
- The signature of OCIMetricsExporter.__init__() changed: You now need to pass a OCIMetricsConverter child object.

### Feat

- introduce MetadataExtractor
- extract OCIMetricsConverter and PrefixedDimensionsExtractor from OCIMetricsExporter

### Refactor

- remove type variable from MetricsConverter protocol
- improve type stubs

## v0.2.3 (2024-08-03)

### Fix

- transform nanoseconds to seconds when parsing OpenTelemetry timestamps

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
