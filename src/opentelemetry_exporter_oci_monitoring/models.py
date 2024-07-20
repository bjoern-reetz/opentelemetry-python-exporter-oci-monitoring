from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from oci import Response  # pyright: ignore[reportMissingTypeStubs]
from oci.monitoring.models import (  # pyright: ignore[reportMissingTypeStubs]
    PostMetricDataResponseDetails,
)

if TYPE_CHECKING:
    from oci.monitoring.models import (  # pyright: ignore[reportMissingTypeStubs]
        FailedMetricRecord,
    )

T = TypeVar("T")


class OCIResponse(Response, Generic[T]):
    data: T


class OCIPostMetricDataResponseDetails(PostMetricDataResponseDetails):
    failed_metrics_count: int  # pyright: ignore[reportIncompatibleMethodOverride]
    failed_metrics: list[FailedMetricRecord]  # pyright: ignore[reportIncompatibleMethodOverride]
