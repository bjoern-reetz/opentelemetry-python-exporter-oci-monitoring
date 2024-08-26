from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import TYPE_CHECKING, Iterator, Mapping, Protocol, Sequence, Union

from oci.monitoring.models import Datapoint, MetricDataDetails
from opentelemetry.sdk.metrics.export import (
    Histogram,
    HistogramDataPoint,
    Metric,
    MetricsData,
    NumberDataPoint,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

if TYPE_CHECKING:
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.util.instrumentation import InstrumentationScope

AttributeValue = Union[
    str, bool, int, float, Sequence[str], Sequence[bool], Sequence[int], Sequence[float]
]
Attributes = Mapping[str, AttributeValue]


logger = getLogger(__name__)

UTC = timezone(timedelta())


class DimensionsExtractor(Protocol):
    def extract(
        self,
        resource: Resource,
        scope: InstrumentationScope,
        data_point: NumberDataPoint | HistogramDataPoint,
    ) -> Mapping[str, str]: ...


def flatten_attribute_value(value: AttributeValue, /) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (bool, int, float)):
        return json.dumps(value)
    return ",".join(flatten_attribute_value(primitive) for primitive in value)


def normalize_attributes(
    attributes: Attributes, /, prefix: str = ""
) -> Mapping[str, str]:
    return {
        prefix + key: flatten_attribute_value(value)
        for key, value in sorted(attributes.items())
    }


@dataclass
class PrefixedDimensionsExtractor(DimensionsExtractor):
    prefix_resource: str = ""
    prefix_scope: str = "scope."

    def extract(
        self,
        resource: Resource,
        scope: InstrumentationScope,
        data_point: NumberDataPoint | HistogramDataPoint,
    ) -> Mapping[str, str]:
        scope_dimensions = {self.prefix_scope + "name": scope.name}
        if scope.version:
            scope_dimensions[self.prefix_scope + "version"] = scope.version

        resource_dimensions = normalize_attributes(
            resource.attributes, prefix=self.prefix_resource
        )

        attribute_dimensions = normalize_attributes(data_point.attributes or {})

        return {**scope_dimensions, **resource_dimensions, **attribute_dimensions}


class MetadataExtractor(Protocol):
    def extract(
        self, resource: Resource, scope: InstrumentationScope, metric: Metric
    ) -> Mapping[str, str] | None: ...


class DefaultMetadataExtractor(MetadataExtractor):
    def extract(
        self,
        resource: Resource,  # noqa: ARG002
        scope: InstrumentationScope,  # noqa: ARG002
        metric: Metric,
    ) -> Mapping[str, str] | None:
        metadata: Mapping[str, str] = {}
        if metric.description:
            metadata["description"] = metric.description
        if metric.unit:
            metadata["unit"] = metric.unit
        return metadata or None


class MetricsConverter(Protocol):
    def convert(self, metrics_data: MetricsData, /) -> Iterator[MetricDataDetails]: ...


@dataclass
class DefaultMetricsConverter(MetricsConverter):
    namespace: str
    resource_group: str
    compartment_id: str

    dimensions_extractor: DimensionsExtractor = field(
        default_factory=PrefixedDimensionsExtractor
    )
    metadata_extractor: MetadataExtractor = field(
        default_factory=DefaultMetadataExtractor
    )

    def convert(self, metrics_data: MetricsData, /) -> Iterator[MetricDataDetails]:
        for resource_metric in metrics_data.resource_metrics:
            resource = resource_metric.resource
            for scope_metric in resource_metric.scope_metrics:
                scope = scope_metric.scope
                for metric in scope_metric.metrics:
                    name = metric.name
                    data = metric.data

                    if isinstance(data, Histogram):
                        logger.warning(
                            "Ignoring histogram metric data: Not implemented.",
                            extra={
                                "metric.name": metric.name,
                                "metric.description": metric.description,
                            },
                        )
                        continue

                    metadata = self.metadata_extractor.extract(resource, scope, metric)

                    metric_data_details_map: Mapping[
                        frozenset[tuple[str, str]], MetricDataDetails
                    ] = {}
                    for data_point in data.data_points:
                        dimensions = self.dimensions_extractor.extract(
                            resource, scope, data_point
                        )

                        key = frozenset(dimensions.items())
                        metric_data_details = metric_data_details_map.get(key)
                        if metric_data_details is None:
                            metric_data_details = MetricDataDetails(
                                namespace=self.namespace,
                                resource_group=self.resource_group,
                                compartment_id=self.compartment_id,
                                name=name,
                                dimensions=dimensions,
                                metadata=metadata,
                                datapoints=[],
                            )
                            metric_data_details_map[key] = metric_data_details

                        datapoint = Datapoint(
                            timestamp=datetime.fromtimestamp(
                                data_point.time_unix_nano / 1e9, tz=UTC
                            ),
                            value=float(data_point.value),
                            count=1,
                        )

                        metric_data_details.datapoints = [
                            *metric_data_details.datapoints,
                            datapoint,
                        ]

                    yield from metric_data_details_map.values()
