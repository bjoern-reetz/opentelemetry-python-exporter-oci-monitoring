from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from opentelemetry_exporter_oci_monitoring.converter import PrefixedDimensionsExtractor
from tests import assert_wellformed_oci_metric_dimensions
from tests.conftest import Attributes


def test_prefixed_dimensions(attributes: Attributes) -> None:
    resource = Resource(attributes=attributes)
    scope = InstrumentationScope(
        name="my-name", version="my-version", schema_url="my-schema"
    )
    extractor = PrefixedDimensionsExtractor()

    dimensions = extractor.extract(resource, scope)
    assert_wellformed_oci_metric_dimensions(dimensions)
    assert dimensions == {
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
        "scope.name": "my-name",
        "scope.version": "my-version",
    }
