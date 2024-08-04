from datetime import datetime
from typing import Literal, Mapping, Sequence

from attrs import define

@define(slots=False, kw_only=True)
class Datapoint:
    count: int | None = 1
    timestamp: datetime
    value: float

@define(slots=False, kw_only=True)
class MetricDataDetails:
    compartment_id: str
    datapoints: Sequence[Datapoint]
    dimensions: Mapping[str, str]
    metadata: Mapping[str, str] | None = None
    name: str
    namespace: str
    resource_group: str | None = None

@define(slots=False, kw_only=True)
class PostMetricDataDetails:
    batch_atomicity: Literal["ATOMIC", "NON_ATOMIC", None] = "NON_ATOMIC"
    metric_data: Sequence[MetricDataDetails]

@define(slots=False, kw_only=True)
class FailedMetricRecord:
    message: str
    metric_data: MetricDataDetails

@define(slots=False, kw_only=True)
class PostMetricDataResponseDetails:
    failed_metrics: list[FailedMetricRecord] | None
    failed_metrics_count: int
