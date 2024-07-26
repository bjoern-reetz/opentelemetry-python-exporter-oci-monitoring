from unittest.mock import NonCallableMock

from oci.monitoring.models import PostMetricDataDetails
from opentelemetry.sdk.metrics.export import MetricExportResult, MetricsData
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter
from tests import assert_wellformed_oci_metric_dimensions
from tests.conftest import Attributes


def test_extract_resource_dimensions(
    oci_metrics_exporter: OCIMetricsExporter, attributes: Attributes
) -> None:
    resource = Resource(attributes=attributes)
    resource_dimensions = oci_metrics_exporter._extract_resource_dimensions(resource)  # pyright: ignore[reportPrivateUsage]

    assert_wellformed_oci_metric_dimensions(resource_dimensions)
    assert resource_dimensions == {
        "a.string": "bar",
        "a.bool": "True",
        "another.bool": "False",
        "an.integer": "-3",
        "another.integer": "15",
        "a.float": "3.3",
        "a.list.of.strings": "('bar', 'bar', 'bar')",
        "a.list.of.bools": "(True, False, True)",
        "a.list.of.integers": "(-3, 5, 42)",
        "a.list.of.floats": "(3.3, -3.3, 0.0)",
    }


def test_extract_scope_dimensions(oci_metrics_exporter: OCIMetricsExporter) -> None:
    scope = InstrumentationScope(
        name="my-name", version="my-version", schema_url="my-schema"
    )
    scope_dimensions = oci_metrics_exporter._extract_scope_dimensions(scope)  # pyright: ignore[reportPrivateUsage]

    assert_wellformed_oci_metric_dimensions(scope_dimensions)
    assert scope_dimensions == {
        "scope.name": "my-name",
        "scope.version": "my-version",
        "scope.schema_url": "my-schema",
    }


def test_convert_metrics(
    oci_metrics_exporter: OCIMetricsExporter, metrics_data: MetricsData
) -> None:
    converted_metric_data = list(oci_metrics_exporter._convert_metrics(metrics_data))  # pyright: ignore[reportPrivateUsage]
    assert len(converted_metric_data) > 0


def test_post_metric_data(
    oci_metrics_exporter: OCIMetricsExporter,
    monitoring_client: NonCallableMock,
    metrics_data: MetricsData,
) -> None:
    result = oci_metrics_exporter.export(metrics_data)
    assert result == MetricExportResult.SUCCESS

    monitoring_client.post_metric_data.assert_called_once_with(
        PostMetricDataDetails(
            metric_data=list(oci_metrics_exporter._convert_metrics(metrics_data)),  # pyright: ignore[reportPrivateUsage]
            batch_atomicity=oci_metrics_exporter.batch_atomicity,
        )
    )
