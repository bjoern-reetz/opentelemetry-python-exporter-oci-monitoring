from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Mapping,
    Protocol,
    Sequence,
    TypeVar,
)

if TYPE_CHECKING:
    from datetime import datetime

    from oci.monitoring.models import (  # pyright: ignore[reportMissingTypeStubs]
        PostMetricDataDetails,
    )


T = TypeVar("T")
U = TypeVar("U")

BATCH_ATOMICITY = Literal["ATOMIC", "NON_ATOMIC"]


class OCIRequest(Protocol, Generic[T]):
    method: str
    url: str
    query_params: Mapping[str, str] | None
    header_params: Mapping[str, str]
    body: T
    response_type: str
    enforce_content_headers: bool


class OCIResponse(Protocol, Generic[T, U]):
    status: int
    headers: Mapping[str, str]
    request: OCIRequest[U]
    next_page: str | None
    request_id: str | None
    has_next_page: bool
    data: T


class OCIDataPoint(Protocol):
    timestamp: datetime
    value: float
    count: int


class OCIMetricDataDetails(Protocol):
    namespace: str
    resource_group: str
    compartment_id: str
    name: str
    dimensions: Mapping[str, str]
    metadata: Mapping[str, str]
    datapoints: Sequence[OCIDataPoint]


class OCIPostMetricDataDetails(Protocol):
    metric_data: list[OCIMetricDataDetails]
    batch_atomicity: BATCH_ATOMICITY


class OCIFailedMetricRecord(Protocol):
    message: str
    metric_data: OCIMetricDataDetails


class OCIPostMetricDataResponseDetails(Protocol):
    failed_metrics_count: int
    failed_metrics: list[OCIFailedMetricRecord]


class OCIMetricsClient(Protocol):
    def post_metric_data(
        self,
        post_metric_data_details: PostMetricDataDetails,
        /,
        opc_request_id: str | None = None,
        content_encoding: str | None = None,
        retry_strategy: Any = None,  # noqa: ANN401
        allow_control_chars: bool | None = None,
    ) -> OCIResponse[OCIPostMetricDataResponseDetails, str]: ...
