# opentelemetry-exporter-oci-monitoring

[![pipeline status](https://github.com/bjoern-reetz/opentelemetry-python-exporter-oci-monitoring/actions/workflows/publish.yml/badge.svg?main)](https://github.com/bjoern-reetz/opentelemetry-exporter-oci-monitoring/actions/workflows/publish.yml)
[![latest package version](https://img.shields.io/pypi/v/opentelemetry-exporter-oci-monitoring)](https://pypi.org/project/opentelemetry-exporter-oci-monitoring/)
[![supported python versions](https://img.shields.io/pypi/pyversions/opentelemetry-exporter-oci-monitoring)](https://www.python.org/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/opentelemetry-exporter-oci-monitoring)](https://pypistats.org/packages/opentelemetry-exporter-oci-monitoring)
[![license](./images/license.svg)](./LICENSE)
[![source files coverage](./images/coverage.svg)](https://coverage.readthedocs.io/)
[![pyright](./images/pyright.svg)](https://microsoft.github.io/pyright)
[![ruff](./images/ruff.svg)](https://docs.astral.sh/ruff)
[![pre-commit](./images/pre-commit.svg)](https://pre-commit.com/)

A Python OpenTelemetry exporter for the OCI Monitoring Service.

```bash
pip install opentelemetry-exporter-oci-monitoring
```

This software is in an early development phase. Feel free to use it at your own risk.

**Histograms are not yet implemented and will be skipped during export.**


```python
from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter

exporter = OCIMetricsExporter(client, namespace, resource_group, compartment_id)
```

Remember to set the service endpoint to a `telemetry-ingestion` URL (e.g. `https://telemetry-ingestion.eu-frankfurt-1.oraclecloud.com`) when creating the metrics client. For more details refer to the [OCI Documentation of PostMetricData API](https://docs.oracle.com/en-us/iaas/api/#/en/monitoring/20180401/MetricData/PostMetricData).
