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
from oci.monitoring import MonitoringClient
from opentelemetry_exporter_oci_monitoring.utils import make_default_exporter

client = MonitoringClient(service_endpoint="https://telemetry-ingestion.eu-frankfurt-1.oraclecloud.com", ...)
exporter = make_default_exporter(client, namespace="my-met-ns", resource_group="my-res-grp", compartment_id="ocid1.compartment.abc123")
```

Remember to set the service endpoint to a `telemetry-ingestion` URL (e.g. `https://telemetry-ingestion.eu-frankfurt-1.oraclecloud.com`) when creating the metrics client. For more details refer to the [OCI Documentation of PostMetricData API](https://docs.oracle.com/en-us/iaas/api/#/en/monitoring/20180401/MetricData/PostMetricData).
