import typing
from dataclasses import InitVar, dataclass, field
from http import HTTPStatus
from logging import getLogger
from typing import Dict, List, Optional

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
from opentelemetry.sdk.resources import Attributes
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

logger = getLogger(__name__)


@dataclass
class OCIMetricsExporter(MetricExporter):
    client: MonitoringClient = field(repr=False)
    namespace: str
    resource_group: str
    compartment_id: str

    preferred_temporality: InitVar[Optional[Dict[type, AggregationTemporality]]] = None
    preferred_aggregation: InitVar[Optional[Dict[type, Aggregation]]] = None

    def __post_init__(
        self,
        preferred_temporality: Optional[Dict[type, AggregationTemporality]],
        preferred_aggregation: Optional[Dict[type, Aggregation]],
    ) -> None:
        # superclass initializer type annotations are lying: it is in fact accepting None
        super().__init__(
            preferred_temporality=typing.cast(
                Dict[type, AggregationTemporality], preferred_temporality
            ),
            preferred_aggregation=typing.cast(
                Dict[type, Aggregation], preferred_aggregation
            ),
        )

    def export(
        self,
        metrics_data: MetricsData,
        timeout_millis: float = 10_000,
        **kwargs: Dict[str, typing.Any],
    ) -> MetricExportResult:
        if len(kwargs) > 0:
            logger.warning(
                "Ignored extra export kwargs.", extra={"ignored_kwargs": kwargs}
            )

        metric_data: List[MetricDataDetails] = []
        for resource_metric in metrics_data.resource_metrics:
            resource = resource_metric.resource
            for scope_metric in resource_metric.scope_metrics:
                scope = scope_metric.scope
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
                        # Datapoint __init__
                        # :type timestamp: datetime
                        # :type value: float
                        # :type count: int
                        Datapoint(
                            timestamp=data_point.time_unix_nano,
                            value=float(data_point.value),
                            count=1,
                        )
                        for data_point in data.data_points
                    ]

                    # MetricDataDetails __init__ params:
                    # param: namespace: str
                    # param: resource_group: str
                    # param: compartment_id: str
                    # param: name: str
                    # param: dimensions: dict(str, str)
                    # param: metadata: dict(str, str)
                    # param: datapoints: list[oci.monitoring.models.Datapoint]
                    MetricDataDetails(
                        namespace=self.namespace,
                        resource_group=self.resource_group,
                        compartment_id=self.compartment_id,
                        name=name,
                        dimensions={
                            **self._attributes_to_dimensions(
                                resource.attributes, prefix="resource."
                            ),
                            **self._scope_to_dimensions(scope),
                        },
                        metadata={"description": description},
                        datapoints=datapoints,
                    )

        post_metric_data_details = PostMetricDataDetails(
            metric_data=metric_data,
            batch_atomicity=PostMetricDataDetails.BATCH_ATOMICITY_NON_ATOMIC,
        )
        response: Response = self.client.post_metric_data(post_metric_data_details)
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
        self, timeout_millis: float = 30_000, **kwargs: Dict[str, typing.Any]
    ) -> None:
        if len(kwargs) > 0:
            logger.warning(
                "Ignored extra shutdown kwargs.", extra={"ignored_kwargs": kwargs}
            )

    @staticmethod
    def _attributes_to_dimensions(
        attributes: Attributes, /, *, prefix: str = ""
    ) -> Dict[str, str]:
        if prefix and not prefix.endswith("."):
            prefix = prefix + "."
        return {f"{prefix}{key}": str(value) for key, value in attributes.items()}

    @staticmethod
    def _scope_to_dimensions(scope: InstrumentationScope, /) -> Dict[str, str]:
        dimensions = {
            "scope.name": scope.name,
        }
        if scope.version:
            dimensions["scope.version"] = scope.version
        if scope.schema_url:
            dimensions["scope.schema_url"] = scope.schema_url
        return dimensions
