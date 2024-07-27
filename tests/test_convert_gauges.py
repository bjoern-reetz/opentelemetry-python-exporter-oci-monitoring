from opentelemetry.sdk.metrics.export import Gauge as GaugePoint
from opentelemetry.sdk.metrics.export import (
    Metric,
    MetricsData,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from opentelemetry_exporter_oci_monitoring import OCIMetricsExporter


def test_convert_gauge(oci_metrics_exporter: OCIMetricsExporter) -> None:
    point = NumberDataPoint({"foo": "bar"}, 123, 456, 42)
    data = GaugePoint(data_points=[point])
    metric = Metric("my-metric-name", description=None, unit=None, data=data)
    scope = InstrumentationScope("scope-name")
    resource = Resource({"name": "foobar"})
    scope_metrics = ScopeMetrics(scope, [metric], schema_url="lorem")
    resource_metric = ResourceMetrics(resource, [scope_metrics], schema_url="lorem")
    metrics_data = MetricsData(resource_metrics=[resource_metric])

    converted_metrics = list(oci_metrics_exporter._convert_metrics(metrics_data))  # pyright: ignore[reportPrivateUsage]
    assert len(converted_metrics) == 1

    converted_gauge_metric = converted_metrics[0]
    assert converted_gauge_metric.namespace == oci_metrics_exporter.namespace
    assert converted_gauge_metric.resource_group == oci_metrics_exporter.resource_group
    assert converted_gauge_metric.compartment_id == oci_metrics_exporter.compartment_id

    datapoint = converted_gauge_metric.datapoints[0]
    assert datapoint.value == float(point.value)
    assert datapoint.count == 1
    assert datapoint.timestamp.timestamp() == float(point.time_unix_nano)
