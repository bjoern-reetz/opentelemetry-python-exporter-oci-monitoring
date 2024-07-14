from unittest.mock import NonCallableMock

from opentelemetry.sdk.metrics.export import MetricsData
from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter


def test_exporter(
    monitoring_client: NonCallableMock, metrics_data: MetricsData
) -> None:
    exporter = OCIMetricsExporter(
        monitoring_client, namespace="foo", resource_group="bar", compartment_id="baz"
    )

    exporter.export(metrics_data)
