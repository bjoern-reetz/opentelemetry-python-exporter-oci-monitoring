from unittest.mock import NonCallableMock

from oci.monitoring.models import PostMetricDataDetails
from opentelemetry.sdk.metrics.export import MetricExportResult, MetricsData

from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter


def test_post_metric_data(
    oci_metrics_exporter: OCIMetricsExporter,
    monitoring_client: NonCallableMock,
    metrics_data: MetricsData,
) -> None:
    result = oci_metrics_exporter.export(metrics_data)
    assert result == MetricExportResult.SUCCESS

    monitoring_client.post_metric_data.assert_called_once_with(
        PostMetricDataDetails(
            metric_data=list(oci_metrics_exporter.converter.convert(metrics_data)),
            batch_atomicity=oci_metrics_exporter.batch_atomicity,
        )
    )
