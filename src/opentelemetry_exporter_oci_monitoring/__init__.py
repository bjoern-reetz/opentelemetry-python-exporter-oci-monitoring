from dataclasses import InitVar, dataclass, field
from http import HTTPStatus
from logging import getLogger
from typing import Any, Dict, Iterator, Optional, cast

from oci import Response
from oci.monitoring import MonitoringClient
from oci.monitoring.models import (
    Datapoint,
    MetricDataDetails,
    PostMetricDataDetails,
    PostMetricDataResponseDetails,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    Histogram,
    MetricExporter,
    MetricExportResult,
    MetricsData,
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

    batch_atomicity: PostMetricDataDetails = (
        PostMetricDataDetails.BATCH_ATOMICITY_ATOMIC
    )

    preferred_temporality: InitVar[Optional[Dict[type, AggregationTemporality]]] = None
    preferred_aggregation: InitVar[Optional[Dict[type, Aggregation]]] = None

    def __post_init__(
        self,
        preferred_temporality: Optional[Dict[type, AggregationTemporality]],
        preferred_aggregation: Optional[Dict[type, Aggregation]],
    ) -> None:
        # superclass initializer type annotations are lying: it is in fact accepting dict | None
        super().__init__(
            preferred_temporality=cast(
                Dict[type, AggregationTemporality], preferred_temporality
            ),
            preferred_aggregation=cast(Dict[type, Aggregation], preferred_aggregation),
        )

    def export(
        self,
        metrics_data: MetricsData,
        timeout_millis: float = 10_000,
        **kwargs: Dict[str, Any],
    ) -> MetricExportResult:
        if len(kwargs) > 0:
            logger.warning(
                "Ignored extra export kwargs.", extra={"ignored_kwargs": kwargs}
            )

        response: Response = self.client.post_metric_data(
            PostMetricDataDetails(
                metric_data=list(self.convert_metrics(metrics_data)),
                batch_atomicity=self.batch_atomicity,
            )
        )

        response_data: PostMetricDataResponseDetails = response.data
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

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        return True

    def shutdown(
        self, timeout_millis: float = 30_000, **kwargs: Dict[str, Any]
    ) -> None:
        if len(kwargs) > 0:
            logger.warning(
                "Ignored extra shutdown kwargs.", extra={"ignored_kwargs": kwargs}
            )

    def convert_metrics(
        self, metrics_data: MetricsData, /
    ) -> Iterator[MetricDataDetails]:
        for resource_metric in metrics_data.resource_metrics:
            resource = resource_metric.resource
            resource_dims = self.extract_resource_dimensions(resource)
            for scope_metric in resource_metric.scope_metrics:
                scope = scope_metric.scope
                scope_dims = self.extract_scope_dimensions(scope)
                for metric in scope_metric.metrics:
                    name = metric.name
                    description = metric.description
                    data = metric.data

                    if isinstance(data, Histogram):
                        logger.warning(
                            "Ignoring histogram metric data: Not implemented.",
                            extra={
                                "data_points": data.data_points,
                                "aggregation_temporality": data.aggregation_temporality,
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

                    yield MetricDataDetails(
                        namespace=self.namespace,
                        resource_group=self.resource_group,
                        compartment_id=self.compartment_id,
                        name=name,
                        dimensions={
                            **resource_dims,
                            **scope_dims,
                        },
                        metadata={"description": description},
                        datapoints=datapoints,
                    )

    def extract_resource_dimensions(self, resource: Resource, /) -> Dict[str, str]:
        return {
            self.dim_prefix_resource + key: str(value)
            for key, value in resource.attributes.items()
        }

    def extract_scope_dimensions(
        self, scope: InstrumentationScope, /
    ) -> Dict[str, str]:
        dimensions = {
            self.dim_prefix_scope + "name": scope.name,
        }
        if scope.version:
            dimensions[self.dim_prefix_scope + "version"] = scope.version
        if scope.schema_url:
            dimensions[self.dim_prefix_scope + "schema_url"] = scope.schema_url
        return dimensions
