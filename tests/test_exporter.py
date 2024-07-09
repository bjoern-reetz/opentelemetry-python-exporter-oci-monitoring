from oci.monitoring import MonitoringClient
from opentelemetry.sdk.metrics.export import MetricsData
from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter


def test_exporter(
    monitoring_client: MonitoringClient, metrics_data: MetricsData
) -> None:
    _ = OCIMetricsExporter(
        monitoring_client, namespace="foo", resource_group="bar", compartment_id="baz"
    )
