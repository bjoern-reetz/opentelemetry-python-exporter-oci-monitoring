from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from http import HTTPStatus
from logging import getLogger
from typing import TYPE_CHECKING, Any, Iterator, cast

from oci.monitoring.models import (  # pyright: ignore[reportMissingTypeStubs]
    Datapoint,
    MetricDataDetails,
    PostMetricDataDetails,
)
from opentelemetry.sdk.metrics._internal.instrument import (
    Counter,
    Gauge,
    Histogram,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricExporter,
    MetricExportResult,
    MetricsData,
)
from opentelemetry.sdk.metrics.export import Histogram as HistogramPoint

from opentelemetry_exporter_oci_monitoring.models import (
    BATCH_ATOMICITY,
    OCIMetricDataDetails,
    OCIMetricsClient,
)

if TYPE_CHECKING:
    from oci.monitoring import (  # pyright: ignore[reportMissingTypeStubs]
        MonitoringClient,
    )
    from opentelemetry.sdk.metrics.view import Aggregation
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.util.instrumentation import InstrumentationScope

logger = getLogger(__name__)


@dataclass
class OCIMetricsExporter(MetricExporter):
    client: MonitoringClient = field(repr=False)
    namespace: str
    resource_group: str
    compartment_id: str

    dim_prefix_resource: str = ""
    dim_prefix_scope: str = "scope."

    batch_atomicity: BATCH_ATOMICITY = "ATOMIC"

    preferred_temporality: InitVar[dict[type, AggregationTemporality] | None] = None
    preferred_aggregation: InitVar[dict[type, Aggregation] | None] = None

    def __post_init__(
        self,
        preferred_temporality: dict[type, AggregationTemporality] | None,
        preferred_aggregation: dict[type, Aggregation] | None,
    ) -> None:
        preferred_temporality = {
            Counter: AggregationTemporality.DELTA,
            Gauge: AggregationTemporality.DELTA,
            Histogram: AggregationTemporality.DELTA,
            ObservableCounter: AggregationTemporality.DELTA,
            ObservableGauge: AggregationTemporality.DELTA,
            ObservableUpDownCounter: AggregationTemporality.DELTA,
            UpDownCounter: AggregationTemporality.DELTA,
            **(preferred_temporality or {}),
        }
        preferred_aggregation = preferred_aggregation or {}

        super().__init__(  # pyright: ignore[reportUnknownMemberType]
            preferred_temporality=preferred_temporality,
            preferred_aggregation=preferred_aggregation,
        )

    def export(
        self,
        metrics_data: MetricsData,
        timeout_millis: float = 10_000,  # noqa: ARG002
        **kwargs: dict[str, Any],
    ) -> MetricExportResult:
        if len(kwargs) > 0:
            logger.warning(
                "Ignored extra export kwargs.", extra={"ignored_kwargs": kwargs}
            )

        response = cast(OCIMetricsClient, self.client).post_metric_data(
            PostMetricDataDetails(
                metric_data=list(self._convert_metrics(metrics_data)),
                batch_atomicity=self.batch_atomicity,
            )
        )

        response_data = response.data
        if response_data.failed_metrics_count > 0:
            logger.warning(
                "Failed exporting some metrics.",
                extra={
                    "failed_metrics": response_data.failed_metrics,
                    "failed_metrics_count": response_data.failed_metrics_count,
                },
            )

        return (
            MetricExportResult.SUCCESS
            if response.status == HTTPStatus.OK
            else MetricExportResult.FAILURE
        )

    def force_flush(self, timeout_millis: float = 10_000) -> bool:  # noqa: ARG002
        return True

    def shutdown(
        self,
        timeout_millis: float = 30_000,  # noqa: ARG002
        **kwargs: dict[str, Any],
    ) -> None:
        if len(kwargs) > 0:
            logger.warning(
                "Ignored extra shutdown kwargs.", extra={"ignored_kwargs": kwargs}
            )

    def _convert_metrics(
        self, metrics_data: MetricsData, /
    ) -> Iterator[OCIMetricDataDetails]:
        for resource_metric in metrics_data.resource_metrics:
            resource = resource_metric.resource
            resource_dims = self._extract_resource_dimensions(resource)
            for scope_metric in resource_metric.scope_metrics:
                scope = scope_metric.scope
                scope_dims = self._extract_scope_dimensions(scope)
                for metric in scope_metric.metrics:
                    name = metric.name
                    description = metric.description
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
                            timestamp=data_point.time_unix_nano,
                            value=float(data_point.value),
                            count=1,
                        )
                        for data_point in data.data_points
                    ]

                    yield cast(
                        OCIMetricDataDetails,
                        MetricDataDetails(
                            namespace=self.namespace,
                            resource_group=self.resource_group,
                            compartment_id=self.compartment_id,
                            name=name,
                            dimensions={**resource_dims, **scope_dims},
                            metadata={"description": description},
                            datapoints=datapoints,
                        ),
                    )

    def _extract_resource_dimensions(self, resource: Resource, /) -> dict[str, str]:
        return {
            self.dim_prefix_resource + key: str(value)
            for key, value in resource.attributes.items()
        }

    def _extract_scope_dimensions(
        self, scope: InstrumentationScope, /
    ) -> dict[str, str]:
        dimensions = {self.dim_prefix_scope + "name": scope.name}
        if scope.version:
            dimensions[self.dim_prefix_scope + "version"] = scope.version
        if scope.schema_url:
            dimensions[self.dim_prefix_scope + "schema_url"] = scope.schema_url
        return dimensions
