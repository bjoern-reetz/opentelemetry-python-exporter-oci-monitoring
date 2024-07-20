from unittest.mock import NonCallableMock

from oci.monitoring.models import (  # pyright: ignore[reportMissingTypeStubs]
    PostMetricDataDetails,
)
from oci.response import Response  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.sdk.metrics.export import MetricExportResult, MetricsData

from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter


def test_exporter(
    monitoring_client: NonCallableMock, metrics_data: MetricsData
) -> None:
    namespace = "foo"
    resource_group = "bar"
    compartment_id = "baz"

    def validate_post_metric_data(
        post_metric_data_details: PostMetricDataDetails,
    ) -> Response:
        assert (
            post_metric_data_details.batch_atomicity  # pyright: ignore[reportUnknownMemberType]
            == PostMetricDataDetails.BATCH_ATOMICITY_ATOMIC
        )
        assert len(post_metric_data_details.metric_data) > 0  # pyright: ignore[reportUnknownMemberType,reportArgumentType]

        return monitoring_client.post_metric_data.return_value

    monitoring_client.configure_mock(
        **{"post_metric_data.side_effect": validate_post_metric_data}
    )

    exporter = OCIMetricsExporter(
        monitoring_client,
        namespace=namespace,
        resource_group=resource_group,
        compartment_id=compartment_id,
    )

    result = exporter.export(metrics_data)
    assert result == MetricExportResult.SUCCESS

    monitoring_client.post_metric_data.assert_called_once()
