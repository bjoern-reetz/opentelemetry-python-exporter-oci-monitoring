from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import TYPE_CHECKING, Iterator, Protocol

from oci.monitoring.models import Datapoint, MetricDataDetails
from opentelemetry.sdk.metrics.export import Histogram as HistogramPoint
from opentelemetry.sdk.metrics.export import Metric, MetricsData
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

if TYPE_CHECKING:
    from collections.abc import Mapping

    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.util.instrumentation import InstrumentationScope

logger = getLogger(__name__)

UTC = timezone(timedelta())


class DimensionsExtractor(Protocol):
    def extract(
        self, resource: Resource, scope: InstrumentationScope
    ) -> Mapping[str, str]: ...


@dataclass
class PrefixedDimensionsExtractor(DimensionsExtractor):
    prefix_resource: str = ""
    prefix_scope: str = "scope."

    def extract(
        self, resource: Resource, scope: InstrumentationScope
    ) -> Mapping[str, str]:
        dimensions = {
            self.prefix_resource + key: str(value)
            for key, value in resource.attributes.items()
        }

        dimensions[self.prefix_scope + "name"] = scope.name
        if scope.version:
            dimensions[self.prefix_scope + "version"] = scope.version

        return dimensions


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

                    if isinstance(data, HistogramPoint):
                        logger.warning(
                            "Ignoring histogram metric data: Not implemented.",
                            extra={
                                "metric.name": metric.name,
                                "metric.description": metric.description,
                            },
                        )
                        continue

                    datapoints = [
                        Datapoint(
                            timestamp=datetime.fromtimestamp(
                                data_point.time_unix_nano / 1e9, tz=UTC
                            ),
                            value=float(data_point.value),
                            count=1,
                        )
                        for data_point in data.data_points
                    ]

                    yield MetricDataDetails(
                        namespace=self.namespace,
                        resource_group=self.resource_group,
                        compartment_id=self.compartment_id,
                        name=name,
                        dimensions=self.dimensions_extractor.extract(resource, scope),
                        metadata=self.metadata_extractor.extract(
                            resource, scope, metric
                        ),
                        datapoints=datapoints,
                    )
