from unittest.mock import NonCallableMock

from oci.monitoring.models import PostMetricDataDetails
from opentelemetry.sdk.metrics.export import MetricExportResult, MetricsData

from opentelemetry_exporter_oci_monitoring import OCIMonitoringExporter


def test_post_metric_data(
    oci_monitoring_exporter: OCIMonitoringExporter,
    monitoring_client: NonCallableMock,
    metrics_data: MetricsData,
) -> None:
    result = oci_monitoring_exporter.export(metrics_data)
    assert result == MetricExportResult.SUCCESS

    monitoring_client.post_metric_data.assert_called_once_with(
        PostMetricDataDetails(
            metric_data=list(oci_monitoring_exporter.converter.convert(metrics_data)),
            batch_atomicity=oci_monitoring_exporter.batch_atomicity,
        )
    )
