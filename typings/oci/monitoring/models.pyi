from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Mapping, Sequence

@dataclass
class Datapoint:
    timestamp: datetime
    value: float
    count: int

@dataclass
class MetricDataDetails:
    namespace: str
    resource_group: str
    compartment_id: str
    name: str
    dimensions: Mapping[str, str]
    metadata: Mapping[str, str]
    datapoints: Sequence[Datapoint]

@dataclass
class PostMetricDataDetails:
    metric_data: Sequence[MetricDataDetails]
    batch_atomicity: Literal["ATOMIC", "NON_ATOMIC"]

@dataclass
class FailedMetricRecord:
    message: str
    metric_data: MetricDataDetails

@dataclass
class PostMetricDataResponseDetails:
    failed_metrics_count: int
    failed_metrics: list[FailedMetricRecord]
