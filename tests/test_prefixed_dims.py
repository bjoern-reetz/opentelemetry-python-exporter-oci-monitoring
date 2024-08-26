from opentelemetry.sdk.metrics.export import NumberDataPoint
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from opentelemetry_exporter_oci_monitoring.converter import (
    Attributes,
    PrefixedDimensionsExtractor,
)
from tests import assert_wellformed_oci_metric_dimensions


def test_prefixed_dimensions(
    attributes: Attributes, number_data_point: NumberDataPoint
) -> None:
    resource = Resource(attributes=dict(attributes))
    scope = InstrumentationScope(
        name="my-name", version="my-version", schema_url="my-schema"
    )
    extractor = PrefixedDimensionsExtractor(prefix_resource="resource.")

    dimensions = extractor.extract(resource, scope, number_data_point)
    assert_wellformed_oci_metric_dimensions(dimensions)

    assert dimensions == {
        "scope.name": "my-name",
        "scope.version": "my-version",
        "resource.a.string": "bar",
        "resource.a.bool": "true",
        "resource.another.bool": "false",
        "resource.an.integer": "-3",
        "resource.another.integer": "15",
        "resource.a.float": "3.3",
        "resource.a.list.of.strings": "bar,bar,bar",
        "resource.a.list.of.bools": "true,false,true",
        "resource.a.list.of.integers": "-3,5,42",
        "resource.a.list.of.floats": "3.3,-3.3,0.0",
        "a.string": "bar",
        "a.bool": "true",
        "another.bool": "false",
        "an.integer": "-3",
        "another.integer": "15",
        "a.float": "3.3",
        "a.list.of.strings": "bar,bar,bar",
        "a.list.of.bools": "true,false,true",
        "a.list.of.integers": "-3,5,42",
        "a.list.of.floats": "3.3,-3.3,0.0",
    }
