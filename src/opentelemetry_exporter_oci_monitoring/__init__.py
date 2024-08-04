from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from http import HTTPStatus
from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal

from oci.monitoring.models import MetricDataDetails, PostMetricDataDetails
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

if TYPE_CHECKING:
    from oci.monitoring import MonitoringClient
    from opentelemetry.sdk.metrics.view import Aggregation

    from opentelemetry_exporter_oci_monitoring.converter import MetricsConverter

logger = getLogger(__name__)

BATCH_ATOMICITY = Literal["ATOMIC", "NON_ATOMIC"]


@dataclass
class OCIMetricsExporter(MetricExporter):
    client: MonitoringClient = field(repr=False)
    converter: MetricsConverter[MetricDataDetails] = field(repr=False)

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

        response = self.client.post_metric_data(
            PostMetricDataDetails(
                metric_data=list(self.converter.convert(metrics_data)),
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
