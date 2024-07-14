from __future__ import annotations

import unittest.mock
from typing import Dict

import pytest
from oci.monitoring import MonitoringClient
from oci.monitoring.models import PostMetricDataResponseDetails
from oci.response import Response
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    Metric,
    MetricsData,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
    Sum,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.util.types import AttributeValue

Attributes = Dict[str, AttributeValue]


@pytest.fixture()
def attributes() -> Attributes:
    return {
        "a.string": "bar",
        "a.bool": True,
        "another.bool": False,
        "an.integer": -3,
        "another.integer": 15,
        "a.float": 3.3,
        "a.list.of.strings": ["bar", "bar", "bar"],
        "a.list.of.bools": [True, False, True],
        "a.list.of.integers": [-3, 5, 42],
        "a.list.of.floats": [3.3, -3.3, 0.0],
    }


@pytest.fixture()
def number_data_point(attributes: Attributes | None) -> NumberDataPoint:
    return NumberDataPoint(
        attributes=attributes,
        start_time_unix_nano=123456789,
        time_unix_nano=12345678910,
        value=42,
    )


@pytest.fixture()
def otel_sum(number_data_point: NumberDataPoint) -> Sum:
    data_points = [number_data_point]
    delta = 100_000
    attributes = number_data_point.attributes
    start_time_unix_nano = number_data_point.start_time_unix_nano
    time_unix_nano = number_data_point.time_unix_nano
    value = number_data_point.value
    for _ in range(12):
        start_time_unix_nano += delta
        time_unix_nano += delta
        data_points.append(
            NumberDataPoint(
                attributes=attributes,
                start_time_unix_nano=start_time_unix_nano,
                time_unix_nano=time_unix_nano,
                value=value,
            )
        )

    return Sum(
        data_points=data_points,
        aggregation_temporality=AggregationTemporality.DELTA,
        is_monotonic=True,
    )


@pytest.fixture()
def metric(otel_sum: Sum) -> Metric:
    return Metric(name="foo.metric", description=None, unit=None, data=otel_sum)


@pytest.fixture()
def scope_metrics(metric: Metric) -> ScopeMetrics:
    metrics = 2 * [metric]
    return ScopeMetrics(
        scope=InstrumentationScope(name="foo.scope"), metrics=metrics, schema_url=""
    )


@pytest.fixture()
def resource_metrics(
    scope_metrics: ScopeMetrics, attributes: Attributes
) -> ResourceMetrics:
    resource = Resource(attributes=attributes)
    return ResourceMetrics(
        resource=resource, scope_metrics=[scope_metrics], schema_url=""
    )


@pytest.fixture()
def metrics_data(resource_metrics: ResourceMetrics) -> MetricsData:
    resource_metrics_list = 2 * [resource_metrics]
    return MetricsData(resource_metrics=resource_metrics_list)


@pytest.fixture()
def post_metrics_data_response() -> Response[PostMetricDataResponseDetails]:
    data = PostMetricDataResponseDetails(failed_metrics_count=0, failed_metrics=[])
    mock = unittest.mock.create_autospec(
        Response,
        # spec_set=True does not work as intended for unknown reasons
        instance=True,
    )
    mock.configure_mock(
        status=200,
        data=data,
    )
    return mock


@pytest.fixture()
def monitoring_client(
    post_metrics_data_response: Response[PostMetricDataResponseDetails],
) -> MonitoringClient:
    mock = unittest.mock.create_autospec(MonitoringClient, spec_set=True, instance=True)
    mock.configure_mock(**{"post_metric_data.return_value": post_metrics_data_response})
    return mock
